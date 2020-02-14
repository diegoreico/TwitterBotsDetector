import logging
import asyncio
import pandas as pd

from typing import List

from sqlalchemy.exc import IntegrityError

from etl.domain.models.contract import Contract
from etl.infraestructure.database.dao.daocontracts import DAOContracts
from etl.domain.services.workservice import WorkService


class ContractsService:

    @staticmethod
    def insert_single_contract(row, dao) -> Contract:

        contract = Contract.from_tuple(row)
        try:
            dao.insert_single_contract(contract)
            return contract
        except IntegrityError:
            logging.error(f'Can not insert employee {contract.id_employee} because '
                          f'is not present on colectivos table')
            return Contract.dummy()

    @staticmethod
    def insert_contracts(data: pd.DataFrame, dao: DAOContracts) -> List[Contract]:

        contracts = [ContractsService.insert_single_contract(value, dao) for value in data.itertuples()]

        contracts = list(filter(lambda x: not Contract.is_dummy(x), contracts))

        return contracts

