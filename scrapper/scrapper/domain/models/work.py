import logging
import json
import pandas as pd
from typing import Optional

from pydantic import BaseModel
from datetime import datetime

from etl.domain.services.utilsservice import UtilService

from etl.domain.models.contract import Contract
from etl.configuration import config

class Work(BaseModel):
    id_empleado: int
    colectivo: Optional[str]
    fecha: datetime
    duracion: float
    esperado: float
    substituido: bool = False
    turn: str
    horas_extras_total: float
    horas_extras_dia: float
    horas_extras_noche: float
    horas_a_compensar: float
    presencia_real: float
    registros_entrada: int
    registros_salida: int
    registros_entrada_manual: int
    registros_salida_manual: int
    registros_totales: int
    registros_manuales: int
    registros_horas: float


    @staticmethod
    def dummy():
        return Work(id_empleado=10,
                    fecha=datetime.today().replace(hour=8),
                    duracion=4.0,
                    esperado=8.0,
                    turn='0',
                    horas_extras_total=0.0,
                    horas_extras_dia=0.0,
                    horas_extras_noche=0.0,
                    horas_a_compensar=0.0,
                    presencia_real=0.0,
                    registros_entrada=0,
                    registros_salida=0,
                    registros_entrada_manual=0,
                    registros_salida_manual=0,
                    registros_totales=0,
                    registros_manuales=0,
                    registros_horas=0)

    @staticmethod
    def from_tuple(row):
        return Work(
            id_empleado=UtilService.fix_employee_id(row.codigo_),
            fecha=UtilService.get_date(row.fecha_),
            duracion=UtilService.get_hour_float(row.horas_normales),
            esperado=UtilService.get_hour_float(row.horas_previstas),
            turn=row.calculated_turn,
            horas_extras_total=UtilService.get_hour_float(row.total_horas_extras),
            horas_extras_dia=UtilService.get_hour_float(row.horas_extras_dia),
            horas_extras_noche=UtilService.get_hour_float(row.horas_extra_noche),
            horas_a_compensar=UtilService.get_hour_float(row.horas_a_compensar),
            presencia_real=UtilService.get_hour_float(row.presencia_real)
        )

    @staticmethod
    def from_tuple_and_work_entries(row, first_turn, work_entries):
        def get_registered_time_from_work_entries():
            registed_time = 0
            if len(work_entries) > 0:
                last_in = None
                for entry in work_entries:
                    if entry['sentido'] == 'E':
                        last_in = entry['marcaje']
                    elif entry['sentido'] == 'S' and not pd.isnull(last_in):
                        registed_time = registed_time + (entry['marcaje'] - last_in)
                        last_in = None
            return registed_time
 
        return Work(
            id_empleado=UtilService.fix_employee_id(row.codigo_),
            fecha=UtilService.get_date(row.fecha_),
            duracion=UtilService.get_hour_float(row.horas_normales),
            esperado=UtilService.get_hour_float(row.horas_previstas),
            turn=first_turn,
            horas_extras_total=UtilService.get_hour_float(row.total_horas_extras),
            horas_extras_dia=UtilService.get_hour_float(row.horas_extras_dia),
            horas_extras_noche=UtilService.get_hour_float(row.horas_extra_noche),
            horas_a_compensar=UtilService.get_hour_float(row.horas_a_compensar),
            presencia_real=UtilService.get_hour_float(row.presencia_real),
            registros_entrada=len([x for x in work_entries if x['sentido'] == 'E']),
            registros_salida=len([x for x in work_entries if x['sentido'] == 'S']),
            registros_entrada_manual=len([x for x in work_entries if x['sentido'] == 'E' and x['manual'] == True]),
            registros_salida_manual=len([x for x in work_entries if x['sentido'] == 'S' and x['manual'] == True]),
            registros_totales=len(work_entries),
            registros_manuales=len([x for x in work_entries if x['manual'] == True]),
            registros_horas=get_registered_time_from_work_entries()
        )

    @staticmethod
    def from_contract(contract: Contract) -> list:
        work_list = []
        start = contract.work_relationship_start
        end = contract.work_relationship_end if not pd.isnull(contract.work_relationship_end) else pd.datetime.today()
        date_to_updates = pd.date_range(start=start, end=end)

        for d in date_to_updates:
            w = Work(
                id_empleado=UtilService.fix_employee_id(contract.id_employee),
                fecha=d.to_pydatetime(),
                duracion=0.0,
                esperado=0.0,
                substituido=True,
                turn='0',
                horas_extras_total=0.0,
                horas_extras_dia=0.0,
                horas_extras_noche=0.0,
                horas_a_compensar=0.0
            )
            work_list.append(w)

        return work_list


class WorkEntry(BaseModel):
    codigo: int
    fecha: datetime
    sentido: str
    marcaje: datetime
    manual: bool

    @staticmethod
    def from_row(row):
        return WorkEntry(
            codigo=row.codigo_,
            fecha=row.fecha_,
            sentido=row.sentido_.lower(),
            marcaje=row.marcaje_,
            manual=row.sentido_.islower()
        )

    @staticmethod
    def from_row_and_work_entry(row, work_entry):
        return WorkEntry(
            codigo=row.codigo_,
            fecha=row.fecha_,
            sentido=work_entry.sentido,
            marcaje=work_entry.marcaje,
            manual=work_entry.manual
        )