import json
import logging
from datetime import datetime
import pandas as pd

from operator import itemgetter

from sqlalchemy.exc import IntegrityError
from typing import List
from etl.domain.models.absence import Absence
from etl.domain.models.contract import Contract

from etl.domain.models.work import Work, WorkEntry
from etl.domain.models.colectivos import Colectivo
from etl.domain.services.utilsservice import UtilService
from etl.infraestructure.database.dao.daodiary import DAODiary
from etl.infraestructure.database.dao.daocolectivos import DAOColectivos

from etl.configuration import config

file = open(config.FILE_TURNS, mode='r')
json_file = file.read()
turns = json.loads(json_file)
for turn in turns:
    start = turn['start'].split(":")
    start_hour = int(start[0])
    start_minute = int(start[1])
    moment = datetime.today().replace(hour=start_hour, minute=start_minute)
    turn['start'] = moment

    end = turn['end'].split(":")
    end_hour = int(end[0])
    end_minute = int(end[1])
    moment = datetime.today().replace(hour=start_hour, minute=start_minute)
    turn['end'] = moment

file.close()


class WorkService:

    @staticmethod
    def filter_day_with_working_hours(data: pd.DataFrame) -> pd.DataFrame:
        filter_idx = data['justificacion_'].apply(lambda x: UtilService.is_number(x) or x == '')
        filtered = data[filter_idx]

        return filtered

    @staticmethod
    def insert_single_work(row, dao: DAODiary) -> int:
        work = Work.from_tuple(row)

        try:
            inserted = dao.insert_single_work(work)
        except IntegrityError:
            inserted = 0
            logging.info(f'Already exists a work entry for employee {work.id_empleado} on date {work.fecha}')

        return inserted

    @staticmethod
    def insert_work(data: pd.DataFrame, dao: DAODiary) -> int:
        work_data = data[~data['marcaje_'].isnull() & ~data['marcaje_1'].isnull()]

        results = [WorkService.insert_single_work(value, dao) for value in work_data.itertuples()]

        insertion_counter = sum(results)

        return insertion_counter

    @staticmethod
    def obtain_colectivos(data: pd.DataFrame, dao: DAOColectivos) -> pd.DataFrame:
        data['colectivo'] = data['codigo_'].apply(lambda x: dao.obtain_colectivo_by_employee_id(int(x)))
        return data

    @staticmethod
    def create_non_existing_colectivos(data: pd.DataFrame, dao: DAOColectivos) -> int:
        created_colectivos = 0

        
        filter_idx = data['colectivo'].isnull()
        data_to_insert = data[filter_idx]

        data_to_insert = data_to_insert[['codigo_', 'apellidos_', 'nombre_']].drop_duplicates()

        colectivos = []
        for row in data_to_insert.itertuples():
            colectivo: Colectivo = Colectivo.build_empty_from_work(row)
            colectivos.append(colectivo)

        created_colectivos = dao.insert_colectivo_list(colectivos)
        
        return created_colectivos

    @staticmethod
    def filter_test_users(data: pd.DataFrame):
        data = data[~data['nombre_'].isin(['TEST', 'TEST2'])]
        return data

  
    @staticmethod
    def get_datetime_columns():
        return [
            'fecha_',
            'marcaje_',
            'marcaje_1',
            'marcaje_2',
            'marcaje_3',
            'horas_previstas',
            'horas_normales',
            'presencia_real',
            'asuntos_propios',
            'libre_disposicion',
            'maternidad_paternidad',
            'horas_compensadas',
            'consulta_medico',
            'asuntos_sindicales',
            'licencias',
            'baja_enfermedad',
            'bajas_accidente',
            'huelga',
            'vacaciones_disfrutadas',
            'permisos_no_retribuidos',
            'total_horas_extras',
            'horas_extras_dia',
            'horas_extra_noche',
            'horas_a_compensar',
            'penosidad',
            'nocturnidad'
        ]

    @staticmethod
    def fix_datetime_columns(data: pd.DataFrame) -> pd.DataFrame:
        for column in WorkService.get_datetime_columns():
            data[column] = pd.to_datetime(data[column])
        return data

    @staticmethod
    def add_work_shifts(data: pd.DataFrame, fixed_time_ranges: bool = True) -> pd.DataFrame:
        def _set_turns_with_half_turn_approach(x: pd.datetime):
            if not pd.isnull(x):
                diffs = [UtilService.get_time_diff_in_minutes(x, turn['start']) for turn in turns]
                #diffs = [x if x > 0 else 99 for x in diffs]
                min_index = min(enumerate(diffs), key=itemgetter(1))[0]
                return str(turns[min_index]['start'].hour) + ':' + str(turns[min_index]['start'].minute)
            else:
                return x

        def _set_turns_with_fixed_approach(x: pd.datetime):
            if not pd.isnull(x):
                x_dt = UtilService.get_hour_datetime(x)
                morning = UtilService.get_start_turn('morning', False)
                afternoon = UtilService.get_start_turn('afternoon', False)
                night = UtilService.get_start_turn('night', False)
                if x_dt >= morning and x_dt < afternoon:
                    return '6:0'
                if x_dt >= afternoon and x_dt < night:
                    return '14:0'
                return '22:0'
            else:
                return x

        if fixed_time_ranges:
            data['calculated_turn'] = data['marcaje_'].apply(lambda x: _set_turns_with_fixed_approach(x))
        else:
            data['calculated_turn'] = data['marcaje_'].apply(lambda x: _set_turns_with_half_turn_approach(x))
        
        logging.info('WORK_SHIFTS: Arranging sparse matrix')
        test = data.set_index(['codigo_', 'fecha_','marcaje_'])
        serie_turns=test[['calculated_turn']].unstack('codigo_').ffill().bfill().stack('codigo_').reset_index().sort_values(['codigo_','fecha_'])['calculated_turn']
        
        logging.info('WORK_SHIFTS: Reordering data (to match matrix with)')
        data = data.sort_values(['codigo_','fecha_'])
        data['calculated_turn'] = serie_turns

        return data

    @staticmethod
    def _data_to_events(data: pd.DataFrame) -> pd.DataFrame:
        df0 = data[['codigo_', 'fecha_', 'justificacion_', 'sentido_', 'marcaje_']]

        df1 = data[['codigo_', 'fecha_', 'justificacion_1', 'sentido_1', 'marcaje_1']].rename(
            columns={'justificacion_1': 'justificacion_', 'sentido_1': 'sentido_', 'marcaje_1': 'marcaje_'}
        )

        df2 = data[['codigo_', 'fecha_', 'justificacion_2', 'sentido_2', 'marcaje_2']].rename(
            columns={'justificacion_2': 'justificacion_', 'sentido_2': 'sentido_', 'marcaje_2': 'marcaje_'}
        )

        df3 = data[['codigo_', 'fecha_', 'justificacion_3', 'sentido_3', 'marcaje_3']].rename(
            columns={'justificacion_3': 'justificacion_', 'sentido_3': 'sentido_', 'marcaje_3': 'marcaje_'}
        )

        events_df = pd.concat([df0, df1, df2, df3])
        return events_df

    @staticmethod
    def create_inout_df(data: pd.DataFrame) -> pd.DataFrame:

        events = WorkService._data_to_events(data)
        inout_df = events[~events['marcaje_'].isnull()]

        return inout_df

    @staticmethod
    def insert_entries(inout_df: pd.DataFrame, dao: DAODiary) -> int:
        work_entries = []

        for row in inout_df.itertuples():
            work_entry = WorkEntry.from_row(row)
            work_entries.append(work_entry)

        inserted_results = dao.insert_work_entries(work_entries)

        return inserted_results

    @staticmethod
    def insert_processed_absences(absences: List[Absence], dao: DAODiary) -> int:
        return dao.insert_multiple_absences(absences)

        '''
        def step(absence: Absence, dao: DAODiary):
            try:
                return dao.insert_single_absence(absence)
            except IntegrityError:
                logging.error(f"Couldn't insert absence: {absence.id_empleado} - {absence.fecha}")
                return 0

        results = [step(absence, dao) for absence in absences]

        inserted = sum(results)

        return inserted
        '''

    @staticmethod
    def insert_processed_work(works: List[Work], dao: DAODiary) -> int:
        return dao.insert_multiple_work_registries(works)

        '''
        def step(work: Work, dao: DAODiary):
            try:
                return dao.insert_single_work(work)
            except IntegrityError:
                logging.error(f"Couldn't insert work: {work.id_empleado} - {work.fecha}")
                return 0

        results = [step(work, dao) for work in works]

        inserted = sum(results)

        return inserted
        '''

    @staticmethod
    def _rearrange_absence_data(data: pd.DataFrame) -> pd.DataFrame:

        common_columns_list = ['asuntos_propios', 'libre_disposicion', 'maternidad_paternidad', 'horas_compensadas',
                               'consulta_medico', 'asuntos_sindicales', 'licencias', 'baja_enfermedad',
                               'bajas_accidente', 'huelga', 'vacaciones_disfrutadas', 'permisos_no_retribuidos',
                               'horas_previstas', 'colectivo', 'calculated_turn']

        c0 = ['codigo_', 'fecha_', 'justificacion_', 'sentido_', 'marcaje_'] + common_columns_list
        df0 = data[c0]

        c1 = ['codigo_', 'fecha_', 'justificacion_1', 'sentido_1', 'marcaje_1'] + common_columns_list
        df1 = data[c1].rename(
            columns={
                'justificacion_1': 'justificacion_',
                'sentido_1': 'sentido_',
                'marcaje_1': 'marcaje_',
            }
        )

        c2 = ['codigo_', 'fecha_', 'justificacion_2', 'sentido_2', 'marcaje_2'] + common_columns_list
        df2 = data[c2].rename(
            columns={
                'justificacion_2': 'justificacion_',
                'sentido_2': 'sentido_',
                'marcaje_2': 'marcaje_',
            }
        )

        c3 = ['codigo_', 'fecha_', 'justificacion_3', 'sentido_3', 'marcaje_3'] + common_columns_list
        df3 = data[c3].rename(
            columns={
                'justificacion_3': 'justificacion_',
                'sentido_3': 'sentido_',
                'marcaje_3': 'marcaje_',
            }
        )

        concatenated_df = pd.concat([df0, df1, df2, df3])

        concatenated_df = concatenated_df[(~concatenated_df['justificacion_'].isnull()) | (~concatenated_df['marcaje_'].isnull())]

        return concatenated_df


    @staticmethod
    def get_absence_causes_array():
        return [
            'asuntos_propios',
            'libre_disposicion',
            'maternidad_paternidad',
            'horas_compensadas',
            'consulta_medico',
            'asuntos_sindicales',
            'licencias',
            'baja_enfermedad',
            'bajas_accidente',
            'huelga',
            'vacaciones_disfrutadas',
            'permisos_no_retribuidos'
            ]

    @staticmethod
    def get_absence_causes_in_a_row(row):
        causes = []
        for cause in WorkService.get_absence_causes_array():
            try:
                if not pd.isnull(getattr(row,cause)):
                    causes.append(cause)
            except:
                logging.error('Unexpected error reading absence cause columns from df row')
        
        return causes

    @staticmethod
    def insert_raw_absences(absences: List[Absence], dao: DAODiary) -> int:
        return WorkService.insert_processed_absences(absences, dao)

    @staticmethod
    def insert_raw_work(work: List[Work], dao: DAODiary) -> int:
        return WorkService.insert_processed_work(work, dao)

    @staticmethod
    def get_justification_array_from_row(row):
        justifications = [
            UtilService.fix_justification(row.justificacion_),
            UtilService.fix_justification(row.justificacion_1),
            UtilService.fix_justification(row.justificacion_2),
            UtilService.fix_justification(row.justificacion_3)
        ]
        return [x for x in justifications if str(x) != 'nan' and str(x) != 'NAN']

    @staticmethod
    def get_justification_column_array_from_row(row):
        columns = [
            Absence.get_cause_column_name_from_justification(str(row.justificacion_)),
            Absence.get_cause_column_name_from_justification(str(row.justificacion_1)),
            Absence.get_cause_column_name_from_justification(str(row.justificacion_2)),
            Absence.get_cause_column_name_from_justification(str(row.justificacion_3))
        ]
        return [x for x in columns if str(x) != 'nan' and str(x) != 'NAN']

    @staticmethod
    def get_work_entries_from_row(row):
        work_entries = [
            {
                "sentido": str(row.sentido_).upper(),
                "marcaje": UtilService.get_hour_float(row.marcaje_),
                "manual": str(row.sentido_).islower() 
            },
            {
                "sentido": str(row.sentido_1).upper(),
                "marcaje": UtilService.get_hour_float(row.marcaje_1),
                "manual": str(row.sentido_1).islower() 
            },
            {
                "sentido": str(row.sentido_2).upper(),
                "marcaje": UtilService.get_hour_float(row.marcaje_2),
                "manual": str(row.sentido_2).islower() 
            },
            {
                "sentido": str(row.sentido_3).upper(),
                "marcaje": UtilService.get_hour_float(row.marcaje_3),
                "manual": str(row.sentido_3).islower() 
            },
        ]
        return [x for x in work_entries if not pd.isnull(x['sentido']) and x['sentido'] != 'nan' and x['sentido'] != 'NAN']

    @staticmethod
    def get_absences_from_row_and_causes(row, justifications, causes):
        absences = []

        justifications = list(set(justifications))

        if len(justifications) == len(causes):
            for justification in justifications:
                absences.append(Absence.from_raw_tuple_and_justification(row, str(justification)))
        
        if len(justifications) > len(causes):
            inserted_justifications_by_causes = [] 
            for justification in justifications:
                justification_column = Absence.get_cause_column_name_from_justification(justification)
                if justification_column not in inserted_justifications_by_causes:
                    absences.append(Absence.from_raw_tuple_and_justification(row, justification))
                    inserted_justifications_by_causes.append(justification_column)
                else:
                    absences.append(Absence.from_raw_tuple_and_justification(row, justification, True))

        if len(justifications) < len(causes):
            for cause in causes:
                absences.append(Absence.from_raw_tuple_and_cause(row, cause))

        return absences

    @staticmethod
    def get_work_from_row_and_causes(row, justification_causes, causes):

        if len(justification_causes) == 0 and len(causes) == 0:
            return Work.from_tuple(row)

        return Work.from_tuple(row)

    @staticmethod
    def get_work_from_row_and_work_entries(row, first_turn, work_entries):
        return Work.from_tuple_and_work_entries(row, first_turn, work_entries)
        

    @staticmethod
    def insert_absences_and_work(sorted_data: pd.DataFrame, dao: DAODiary) -> int:

        absences = []
        work = []

        # aux variables for the loop
        last_row = None
        first_turn = None
        last_date = datetime.now()
        justification_causes = []
        causes = []
        work_entries = []

        for row in sorted_data.itertuples():
            if getattr(row, 'fecha_') != last_date:

                if last_row != None:

                    # Insert the last absence registries (it would be possible two or more absences by day)
                    absences.extend(WorkService.get_absences_from_row_and_causes(last_row, justification_causes, causes))

                    # Insert the last work registry (only a registry by day)
                    if not pd.isnull(last_row.horas_normales):
                        new_work = WorkService.get_work_from_row_and_work_entries(last_row, first_turn, work_entries)
                        if new_work != None:
                            work.append(new_work)

                    # Insert the last work_entries


                # Reset data
                last_date = getattr(row, 'fecha_')
                last_row = row
                first_turn = row.calculated_turn
                justification_causes = WorkService.get_justification_array_from_row(row)
                causes = WorkService.get_absence_causes_in_a_row(row)
                work_entries = WorkService.get_work_entries_from_row(row)
            else:

                # Update the justifcation causes
                justification_causes.extend(WorkService.get_justification_array_from_row(row))

                # Update the causes
                causes.extend(WorkService.get_absence_causes_in_a_row(row))

                # Update the work entries
                work_entries.extend(WorkService.get_work_entries_from_row(row))

                # Update the last row (saving the calculated_turn of the first row)
                if (first_turn == None):
                    first_turn = row.calculated_turn 
                last_row = row
                 
        return (WorkService.insert_raw_absences(absences, dao), WorkService.insert_raw_work(work, dao))


    @staticmethod
    def set_work_substitutions(contracts: List[Contract], dao: DAODiary):

        def step(contract, dao):
            work_list_to_update = Work.from_contract(contract)
            for work in work_list_to_update:
                dao.update_substitution(work)

        [step(contract, dao) for contract in contracts]

