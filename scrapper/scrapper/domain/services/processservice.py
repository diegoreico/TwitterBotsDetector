import asyncio
import logging
import pandas as pd

from typing import Dict

from sqlalchemy.exc import IntegrityError

from etl.domain.models.absence import Process
from etl.infraestructure.database.dao.daoprocesses import DAOProcesses


class ProcessService:

    @staticmethod
    def insert_process_for_date(row, date, dao):
        p = Process.from_tuple(row, date)
        try:
            return dao.insert_single_process(p)
        except IntegrityError:
            logging.error(f'Employee with code {p.id_employee} does not exists on colectivos')
            return 0

    @staticmethod
    def insert_processes(data: pd.DataFrame, dao: DAOProcesses) -> int:
        
        processes = []
        for row in data.itertuples():
            dates = pd.date_range(start=row.inicio, end=row.fin if not pd.isnull(row.fin) else pd.datetime.today())
            processes.extend([Process.from_tuple(row, date) for date in dates])
        return dao.insert_multiple_processes(processes)
    """ 
    @staticmethod
    def insert_processes_dates(data: pd.DataFrame, dao: DAOProcessesDates) -> int:
        
        inserted = 0
        for row in data.itertuples():
            dates = pd.date_range(start=row.inicio, end=row.fin if not pd.isnull(row.fin) else pd.datetime.today())

            result = [ProcessService.insert_process_for_date(row, d, dao) for d in dates]
            inserted += sum(result)

        return inserted

    @staticmethod
    def insert_processes_raw(data: pd.DataFrame, dao: DAOProcessesRaw) -> int:
        
        inserted = 0
        for row in data.itertuples():
            dates = pd.date_range(start=row.inicio, end=row.fin if not pd.isnull(row.fin) else pd.datetime.today())

            result = [ProcessService.insert_process_for_date(row, d, dao) for d in dates]
            inserted += sum(result)

        return inserted """

