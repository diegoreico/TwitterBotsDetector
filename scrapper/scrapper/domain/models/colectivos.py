import json
import logging
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel

from etl.domain.services.utilsservice import UtilService
from etl.configuration import config

file = open(config.FILE_COLECTIVOS_CODE_TO_COLUMNS, mode='r')
json_file = file.read()
colectivos_codes_to_names = json.loads(json_file)
file.close()

file = open(config.FILE_DICTIONARIES, mode='r')
json_file = file.read()
dictionaries = json.loads(json_file)
file.close()


class Colectivo(BaseModel):
    id_empleado: int
    unidad_operativa: str
    nombre_unidad_operativa: str
    apellidos: str
    nombre: str
    fecha_alta: Optional[datetime]
    fecha_antiguedad: Optional[datetime]
    antiguedad: Optional[str]
    fecha_nacimiento: Optional[datetime]
    edad: Optional[int]
    dni: Optional[str]
    sexo: Optional[str]
    business_unit: Optional[str]
    business_unit_name: Optional[str]
    departamento: Optional[str]
    departamento_name: Optional[str]
    seccion: Optional[str]
    seccion_name: Optional[str]
    colectivo: Optional[str]
    clave_contrato_codigo: Optional[str]
    clave_contrato: Optional[str]
    clase_contrato_codigo: Optional[str]
    clase_contrato: Optional[str]
    categoria_codigo: Optional[str]
    categoria: Optional[str]
    active: bool
    familia: str

    @staticmethod
    def dummy():
        return Colectivo(
            id_empleado=0,
            unidad_operativa='not provided',
            nombre_unidad_operativa='not provided',
            apellidos='not provided',
            nombre='not provided',
            fecha_alta=datetime.today(),
            fecha_antiguedad=datetime.today(),
            antiguedad='not provided',
            fecha_nacimiento=datetime.today(),
            edad=0,
            dni='not provided',
            sexo='not provided',
            business_unit='not provided',
            business_unit_name='not provided',
            departamento='not provided',
            departamento_name='not provided',
            seccion='not provided',
            seccion_name='not provided',
            colectivo='not provided',
            clave_contrato_codigo='not provided',
            clave_contrato='not provided',
            clase_contrato_codigo='not provided',
            clase_contrato='not provided',
            categoria_codigo='not provided',
            categoria='not provided',
            active=True,
            familia='not provided'
        )

    @staticmethod
    def fix_op_unit(op_unit: str):
        return str(op_unit).replace(' ','')

    @staticmethod
    def get_family_from_category_code(category_code: str):
        return UtilService.get_from_dictionary('team', 'family_flatten', str(category_code), 'No especificada')

    @staticmethod
    def get_business_unit_name_from_op_unit(op_unit: str):
        return UtilService.get_from_dictionary('team', 'reporting_unit_name', Colectivo.fix_op_unit(op_unit), 'No especificada')

    @staticmethod
    def get_business_unit_code_from_op_unit(op_unit: str):
        return UtilService.get_from_dictionary('team', 'reporting_unit_code', str(op_unit), str(op_unit)[:3])

    @staticmethod
    def get_department_code_from_op_unit(op_unit: str):
        return str(op_unit)[3:].split(" ")[0]

    @staticmethod
    def get_department_name_from_op_unit(op_unit: str):
        return UtilService.get_from_dictionary('team', 'department_name', Colectivo.fix_op_unit(op_unit), 'No especificada')

    @staticmethod
    def get_section_code_from_op_unit(op_unit: str):
        splitted_op_unit = str(op_unit)[3:].split(" ")
        if len(splitted_op_unit) == 2:
            return splitted_op_unit[1]
        return "0"

    @staticmethod
    def get_section_name_from_op_unit(op_unit: str):
        return UtilService.get_from_dictionary('team', 'section_name', Colectivo.fix_op_unit(op_unit), 'No especificada')

    @staticmethod
    def get_name_from_complete_name(surname_and_name: str):
        return surname_and_name.split(",")[1]

    @staticmethod
    def get_surname_from_complete_name(surname_and_name: str):
        return surname_and_name.split(",")[0]


    @staticmethod
    def from_tuple(row, active: bool = True):

        logging.warning('From tuple')

        # special cases
        f_nacimiento = row.f_nacimiento
        if row.edad == 0:
            f_nacimiento = datetime.today()

        colectivo = Colectivo(**{
            'id_empleado': row.emp,
            'unidad_operativa': row.u_op,
            'nombre_unidad_operativa': row.u_operativa,
            'apellidos': Colectivo.get_surname_from_complete_name(row.apellidos_y_nombre),
            'nombre': Colectivo.get_name_from_complete_name(row.apellidos_y_nombre),
            'fecha_alta': row.f_alta,
            'fecha_antiguedad': row.f_antiguedad,
            'antiguedad': row.antig,
            'fecha_nacimiento': f_nacimiento,
            'edad': row.edad,
            'dni': row.dni,
            'sexo': row.sexo,
            'business_unit': Colectivo.get_business_unit_code_from_op_unit(row.u_op),
            'business_unit_name': Colectivo.get_business_unit_name_from_op_unit(row.u_op),
            'departamento': Colectivo.get_department_code_from_op_unit(row.u_op),
            'departamento_name': Colectivo.get_department_name_from_op_unit(row.u_op),
            'seccion': Colectivo.get_section_code_from_op_unit(row.u_op),
            'seccion_name': Colectivo.get_section_name_from_op_unit(row.u_op),
            'colectivo': row.colectivo,
            'clave_contrato_codigo': row.clave_cont,
            'clave_contrato': row.clave_contrato,
            'clase_contrato_codigo': row.clase_cont,
            'clase_contrato': row.clase_contrato,
            'categoria_codigo': row.cat,
            'categoria': row.categoria,
            'active': active,
            'familia': Colectivo.get_family_from_category_code(row.cat)
        })

        return colectivo

    @staticmethod
    def build_empty_from_work(row):
        return Colectivo.dummy().copy(update={
            'id_empleado': row.codigo_,
            'apellidos': row.apellidos_,
            'nombre': row.nombre_
        })

