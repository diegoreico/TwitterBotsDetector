import logging
import pandas as pd
from pydantic import BaseModel
from datetime import datetime

from typing import Optional


class Contract(BaseModel):
    id_employee: int
    work_relationship: str
    contract_code: str
    contract: str
    contract_type_code: str
    contract_type: str
    work_relationship_start: datetime
    work_relationship_end: Optional[datetime]
    contract_start: datetime
    contract_end: Optional[datetime]

    @staticmethod
    def is_dummy(contract):
        return contract.id_employee == 0

    @staticmethod
    def dummy():
        return Contract(
            id_employee=0,
            work_relationship='none',
            contract_code=0,
            contract='none',
            contract_type_code=0,
            contract_type='none',
            work_relationship_start=datetime.today(),
            work_relationship_end=datetime.today(),
            contract_start=datetime.today(),
            contract_end=datetime.today()
        )

    @staticmethod
    def from_tuple(row):

        return Contract(
            id_employee=row.empleado,
            work_relationship=row.relacion_laboral,
            contract_code=row.clave_de_contrato,
            contract=row.den_clave_contrato,
            contract_type_code=row.tipo_de_contrato,
            contract_type=row.den_tipo_contrato,
            work_relationship_start=row.fecha_inicio_rl,
            work_relationship_end=row.fecha_fin_rl if not pd.isnull(row.fecha_fin_rl) else None,
            contract_start=row.f_inicio_contrato,
            contract_end=row.f_fin_contrato if not pd.isnull(row.f_fin_contrato) else None
        )
