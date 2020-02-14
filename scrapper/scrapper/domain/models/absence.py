import sys
import logging
import json
import pandas as pd
from typing import Optional

from etl.configuration import config
from etl.domain.services.utilsservice import UtilService
from pydantic import BaseModel
from datetime import datetime

class Absence(BaseModel):
    id_empleado: int
    colectivo: Optional[str]
    fecha: datetime
    tipo: str
    tipo_agrupado: str
    justificacion: str
    duracion: float
    diacompleto: bool
    categoria_ausencia: str
    codigo_categoria_ausencia: int
    turn: str
    es_prevista: bool

    @staticmethod
    def dummy():
        return Absence(id_empleado=0,
                       fecha=datetime.today(),
                       tipo='test',
                       tipo_agrupado='test',
                       justificacion='test justificacion',
                       duracion=8.0,
                       diacompleto=True,
                       categoria_ausencia='NO_ABSENTISMO',
                       codigo_categoria_ausencia=10,
                       turn='0',
                       es_prevista=False)

    @staticmethod
    def is_full_day_absence(justification: str):
        return not UtilService.is_number(justification)

    @staticmethod
    def is_planned_absence(justification_or_cause: str):
        return UtilService.get_from_dictionary('absence', 'planned', justification_or_cause, False)

    @staticmethod   
    def get_cause_column_name_from_justification(justification: str):
        return UtilService.get_from_dictionary('absence', 'cause_columns', justification, 'CUSTOM_COLUMN_CALCULATED')

    @staticmethod   
    def get_cause_name_from_justification_code(justification_code: str):
        return UtilService.get_from_dictionary('absence', 'name', str(int(float(justification_code))), 'No especificada')

    @staticmethod   
    def get_cause_name_from_justification(justification: str):
        try:
            return get_cause_name_from_justification_code(justification)
        except:
            return justification
        return 'No especificada'


    @staticmethod   
    def get_type_from_cause(cause: str):
        return UtilService.get_from_dictionary('absence', 'cause_justifications', cause, 'No especificada')

    @staticmethod   
    def get_plain_cause_from_justification_or_cause(justification_or_cause: str):
        return UtilService.get_from_dictionary('absence', 'name_flatten', justification_or_cause, 'No especificada')

    @staticmethod   
    def get_absence_category_name_from_justification_or_cause(justification_or_cause: str):
        return UtilService.get_from_dictionary('absence', 'category_name', justification_or_cause, 'NO_ABSENTISMO')

    @staticmethod   
    def get_absence_category_threshold_from_justification_or_cause(justification_or_cause: str):
        return UtilService.get_from_dictionary('absence', 'category_threshold', justification_or_cause, 10)

    @staticmethod   
    def get_full_day_absence_duration_in_hours(row):
        cause_column = Absence.get_cause_column_name_from_justification(str(row.justificacion_))
        if cause_column == 'CUSTOM_COLUMN_FULL_DAY':
            return 8

        if cause_column == 'CUSTOM_COLUMN_CALCULATED':
            return 8
        try:
            duration = row._asdict()[cause_column]
            if not pd.isnull(duration):
                return UtilService.hours_to_float(duration)
        except:
            logging.error(sys.exc_info()[0])

        return 8

    

    @staticmethod
    def get_justification_array(row):
        return [
            str(int(row.justificacion_)),
            str(int(row.justificacion_1)),
            str(int(row.justificacion_2)),
            str(int(row.justificacion_3))
        ]

    @staticmethod
    def get_justification_column_array_(row):
        return [
            Absence.get_cause_column_name_from_justification(str(row.justificacion_)),
            Absence.get_cause_column_name_from_justification(str(row.justificacion_1)),
            Absence.get_cause_column_name_from_justification(str(row.justificacion_2)),
            Absence.get_cause_column_name_from_justification(str(row.justificacion_3))
        ]

    @staticmethod
    def get_duration_from_justification(row, justification):

        def get_duration_for_riesgo_embarazo():
            duration = Absence.get_duration_from_column(row, 'maternidad_paternidad')
            if duration > 0:
                return duration
            return 8

        def get_duration_for_lactancia():
            return Absence.get_duration_from_column(row, 'horas_previstas') - Absence.get_duration_from_column(row, 'horas_normales')

        def get_duration_for_aprobacion_manager():
            return 8 - Absence.get_duration_from_column(row, 'horas_previstas')

        def get_duration_generica():
            previstas = Absence.get_duration_from_column(row, 'horas_previstas')
            presencia = Absence.get_duration_from_column(row, 'horas_presencia')
            diff = previstas - presencia 
            if diff == 0:
                if previstas == 0:
                    return 8
                return previstas
            else:
                return diff

        duration_column = Absence.get_cause_column_name_from_justification(str(justification))

        if duration_column == 'CUSTOM_COLUMN_CALCULATED':

            # Suspensión riesgo de embarazo
            if str(justification) == 'Suspensión por Riesgo Emba' or str(justification) == '43':
                return get_duration_for_riesgo_embarazo()

            # Lactancia
            if str(justification) == 'Permiso lactancia' or str(justification) == '38':
                return get_duration_for_lactancia()

            # Aprobación manager
            if str(justification) == 'Aprobacion Manager' or str(justification) == '46':
                return get_duration_for_aprobacion_manager()
            return get_duration_generica()

        return Absence.get_duration_from_column(row, duration_column)

    @staticmethod
    def get_duration_from_column(row, column):
        try:
            duration = row._asdict()[column]
            if not pd.isnull(duration):
                return UtilService.get_hour_float(duration)
        except:
            logging.error(sys.exc_info()[0])

        return 0


    @staticmethod
    def from_raw_tuple_and_justification(row, justification, no_duration = False):

        if no_duration:
            duration = 0
        else:
            duration = Absence.get_duration_from_justification(row, str(justification))
        is_full_day = duration >= 8
        return Absence(
            id_empleado=UtilService.fix_employee_id(row.codigo_),
            fecha=UtilService.get_date(row.fecha_),
            tipo=Absence.get_cause_name_from_justification(UtilService.fix_justification(justification)),
            tipo_agrupado=Absence.get_plain_cause_from_justification_or_cause(justification),
            justificacion=UtilService.fix_justification(justification),
            duracion=duration,
            diacompleto=is_full_day,
            categoria_ausencia=Absence.get_absence_category_name_from_justification_or_cause(justification),
            codigo_categoria_ausencia=Absence.get_absence_category_threshold_from_justification_or_cause(justification),
            turn=row.calculated_turn,
            es_prevista=Absence.is_planned_absence(justification)
        )

    @staticmethod
    def from_raw_tuple_and_cause(row, cause, justification = ''):

        duration = Absence.get_duration_from_column(row, cause)
        is_full_day = duration >= 8
        return Absence(
            id_empleado=UtilService.fix_employee_id(row.codigo_),
            fecha=UtilService.get_date(row.fecha_),
            tipo=Absence.get_type_from_cause(cause),
            tipo_agrupado=Absence.get_plain_cause_from_justification_or_cause(cause),
            justificacion=justification,
            duracion=duration,
            diacompleto=is_full_day,
            categoria_ausencia=Absence.get_absence_category_name_from_justification_or_cause(cause),
            codigo_categoria_ausencia=Absence.get_absence_category_threshold_from_justification_or_cause(cause),
            turn=row.calculated_turn,
            es_prevista=Absence.is_planned_absence(cause)
        )

    @staticmethod
    def from_raw_tuple(row):

        for justification in Absence.get_justification_array(row):
            if Absence.get_cause_column_name_from_justification(justification) == row.cause:
                duration = Absence.get_duration_from_justification(row, justification)
                is_full_day = duration >= 8
                return Absence(
                    id_empleado=UtilService.fix_employee_id(row.codigo_),
                    fecha=UtilService.get_date(row.fecha_),
                    tipo=Absence.get_cause_name_from_justification(UtilService.fix_justification(justification)),
                    tipo_agrupado=Absence.get_plain_cause_from_justification_or_cause(justification),
                    justificacion=UtilService.fix_justification(justification),
                    duracion=duration,
                    diacompleto=is_full_day,
                    categoria_ausencia=Absence.get_absence_category_name_from_justification_or_cause(justification),
                    codigo_categoria_ausencia=Absence.get_absence_category_threshold_from_justification_or_cause(justification),
                    turn=row.calculated_turn,
                    es_prevista=Absence.is_planned_absence(justification)
                )


class Process(BaseModel):
    id_employee: int
    date: datetime
    hours: int
    process_code: int
    name: str
    process_id: str
    process_start: datetime
    process_end: datetime
    process_hours: int
    process_n_days: int
    process_l_days: int
    cause: str

    @staticmethod
    def dummy():
        return Process(
            id_employee=0,
            date=datetime.today(),
            hours=0,
            process_code=0,
            name='none',
            process_id=-1,
            process_start=datetime.today(),
            process_end=datetime.today(),
            process_hours=0,
            process_n_days=0,
            process_l_days=0,
            cause='none'
        )

    @staticmethod   
    def generate_id(row):
        return str(int(row.empleado)) + '-' +row.inicio.strftime("%Y%m%d")

    @staticmethod   
    def get_cause_from_name(name: str):
        return UtilService.get_from_dictionary('process', 'type_flatten', name, 'No especificada')

    @staticmethod   
    def fix_labour_days(labour_days: int):
        if labour_days > 0:
            return labour_days
        
        return -1

    @staticmethod
    def from_tuple(row, date=None):
        return Process(
            id_employee=UtilService.fix_employee_id(row.empleado),
            date=date if date is not None else row.inicio,
            hours=8,
            process_code=row.proceso,
            name=row.nombre_simbolico,
            process_id=Process.generate_id(row),
            process_start=row.inicio,
            process_end=row.inicio,
            process_hours=row.horas,
            process_n_days=row.dias_nat,
            process_l_days=Process.fix_labour_days(row.dias_lab),
            cause=Process.get_cause_from_name(row.nombre_simbolico)
        )


class ProcessRaw(BaseModel):
    id_employee: int
    date: datetime
    hours: int
    process_code: int
    name: str
    process_id: int
    process_start: datetime
    process_end: datetime
    process_hours: int
    process_n_days: int
    process_l_days: int

    @staticmethod
    def dummy():
        return Process(
            id_employee=0,
            date=datetime.today(),
            hours=0,
            process_code=0,
            name='none',
            process_id='-1',
            process_start=datetime.today(),
            process_end=datetime.today(),
            process_hours=0,
            process_n_days=0,
            process_l_days=0,
        )

    @staticmethod   
    def generate_id(row):
        return str(row.empleado) + row.inicio.strftime("%Y%m%d")

    @staticmethod
    def from_tuple(row, date=None):
        return Process(
            id_employee=row.empleado,
            date=date if date is not None else row.inicio,
            hours=8,
            process_code=row.proceso,
            name=row.nombre_simbolico,
            process_id=Process.generate_id(row),
            process_start=row.inicio,
            process_end=row.inicio,
            process_hours=row.horas,
            process_n_days=row.dias_nat,
            process_l_days=row.dias_lab
        )

