from datetime import datetime
import logging
import json
import pandas as pd

from etl.configuration import config

from etl.infraestructure.database.dao.daodates import DAODates

file = open(config.FILE_DICTIONARIES, mode='r')
json_file = file.read()
dictionaries = json.loads(json_file)
file.close()

class UtilService:

    @staticmethod
    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    @staticmethod
    def get_start_turn(partial: str, real: bool = True):
        if partial == 'morning':
            if real:
                return datetime(2016, 12, 8, 6, 0, 0)
            else:
                return datetime(2016, 12, 8, 5, 0, 0)

        if partial == 'afternoon':
            if real:
                return datetime(2016, 12, 8, 14, 0, 0)
            else:
                return datetime(2016, 12, 8, 13, 0, 0)

        if partial == 'night':
            if real:
                return datetime(2016, 12, 8, 22, 0, 0)
            else:
                return datetime(2016, 12, 8, 21, 0, 0)
        
        return datetime(2016, 12, 8, 6, 0, 0)



    @staticmethod
    def get_date(date_in_row):
        return datetime.today().replace(
            year=date_in_row.year,
            month=date_in_row.month,
            day=date_in_row.day,
            hour=0,
            minute=0,
            second=0,
            microsecond=0)

    @staticmethod
    def get_hour_datetime(hour):
        return datetime(2016, 12, 8, int(hour.hour), int(hour.minute), int(hour.second), 0)

    @staticmethod
    def get_hour_float(hour):
        if not pd.isnull(hour):
            return int(hour.hour) + int(hour.minute) / 60
        return 0

    @staticmethod
    def fix_justification(justification):
        try:
            return str(int(float(justification)))
        except ValueError:
            return str(justification)


    @staticmethod
    def get_time_diff_in_minutes(working_day_start: datetime, turn_start: datetime):

        def get_start_minute(date: datetime):
            return 60 * date.hour + date.minute

        working_day_start_minute = get_start_minute(working_day_start)
        turn_start_minute = get_start_minute(turn_start)

        diff = working_day_start_minute - turn_start_minute

        if abs(diff) < 60 * 8:
            return abs(diff)

        return diff % (60 * 24)

    @staticmethod
    def fix_employee_id(employee_code: str):
        # Miguel Suárez Pintor
        if int(employee_code) == 47529:
            return 1992

        # David Lima Astor
        if int(employee_code) == 47528:
            return 1996
        
        # José Ignacio Parada González-Zaera
        if int(employee_code) ==47488:
            return 1993

        # María Isabel Méndez Calvo
        if int(employee_code) == 8353:
            return 1759

        return int(employee_code)


    @staticmethod
    def get_from_dictionary(section:str, subsection:str, key: str, default: str):
        dictionary = None

        try:
            dictionary = dictionaries[section][subsection]
        except KeyError:
            return default

        # Fix justification if it is a number
        return str(dictionary.get(UtilService.fix_justification(key), dictionary.get('default', default)))


    @staticmethod
    def insert_multiple_dates_from_column(data: pd.DataFrame, column: str, dao: DAODates, bulk: bool = True):
        if bulk:
            return dao.insert_multiple_dates(data[column].unique())

        return dao.insert_multiple_dates(data[column].unique())

    @staticmethod
    def insert_multiple_dates_from_range(data: pd.DataFrame, start: str, end: str, dao: DAODates, bulk: bool = True):
        dates = None
        
        for row in data.itertuples():
            if dates is None:
                logging.info('Fist row')
                logging.info(row.empleado)
                dates = pd.date_range(start=getattr(row, start), end=getattr(row, end) if not pd.isnull(getattr(row, end)) else pd.datetime.today())
            else:
                logging.info('Other row')
                logging.info(row.empleado)
                dates = dates.union(pd.date_range(start=getattr(row, start), end=getattr(row, end) if not pd.isnull(getattr(row, end)) else pd.datetime.today()))
        
        if bulk:
            return dao.insert_multiple_dates(dates.unique())

        for date in dates.unique():
            dao.insert_single_date(date)

        return  