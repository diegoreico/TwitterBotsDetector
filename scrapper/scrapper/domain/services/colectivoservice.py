import logging
import asyncio

from typing import List

import pandas as pd
from etl.domain.models.colectivos import Colectivo
from etl.infraestructure.database.dao.daocolectivos import DAOColectivos


class ColectivoService:

    @staticmethod
    def insert_single_colectivo_row(row, dao: DAOColectivos) -> int:
        colectivo = Colectivo.from_tuple(row, active=True)
        logging.debug(f'trying to insert one element from colectivo')

        inserted = dao.insert_colectivo(colectivo)

        return inserted

    @staticmethod
    def insert_colectivos(colectivos: pd.DataFrame, dao: DAOColectivos) -> int:

        results = [ColectivoService.insert_single_colectivo_row(value, dao) for value in colectivos.itertuples()]

        inserted_counter = sum(results)

        return inserted_counter

    @staticmethod
    def update_single_colectivo_row(row, dao: DAOColectivos, active: bool = True) -> int:
        colectivo = Colectivo.from_tuple(row, active)
        logging.debug(f'trying to update one element from colectivo')

        inserted = dao.update_colectivo(colectivo)

        return inserted

    @staticmethod
    def update_colectivos(colectivos: pd.DataFrame, dao: DAOColectivos, active: bool = True) -> int:

        results = [ColectivoService.update_single_colectivo_row(value, dao, active) for value in colectivos.itertuples()]

        updated_counter = sum(results)

        return updated_counter

    @staticmethod
    def split_by_existence_in_list(data: pd.DataFrame, filter_ids: List[int]) -> (pd.DataFrame, pd.DataFrame):

        no_exists = data[~data['emp'].isin(filter_ids)]
        exists = data[data['emp'].isin(filter_ids)]

        return exists, no_exists

    @staticmethod
    def ids_not_in_data(ids: List[int], data: pd.DataFrame) -> pd.DataFrame:

        not_in = []
        active = data['emp'].to_list()
        for i in ids:
            if i not in active:
                not_in.append(i)

        filtered = data[data['emp'].isin(not_in)]

        return filtered

    @staticmethod
    def upsert(colectivos: pd.DataFrame, dao: DAOColectivos) -> int:
        logging.warning('Upserting')
        logging.warning(colectivos)
        results = [dao.upsert(Colectivo.from_tuple(value, True)) for value in colectivos.itertuples()]

        updated_counter = sum(results)

        return updated_counter