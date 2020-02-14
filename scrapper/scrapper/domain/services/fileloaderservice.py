import subprocess
import unidecode
import pandas as pd
import logging
import os
import datetime

class FileLoaderService:


    @staticmethod
    def load_excel_file(src: str) -> pd.DataFrame:
        logger = logging.getLogger('absbw')

        logger.warning('reading Excel')
        data = pd.read_excel(src, na_values='str')
        logger.warning('before reading')
        new_columns = list(map(lambda x: unidecode.unidecode(x.replace(" ", "_").replace(".", "").lower()), data.columns))
        logger.warning('new_columns_created')
        data.columns = new_columns

        return data

    @staticmethod
    def load_SPED_file_with_cleaning(src: str) -> pd.DataFrame:
        logger = logging.getLogger('absbw')
        logger.info('Reading Excel with cleaning')

        dtype = {
            'marcaje_': str,
            'marcaje_1': str,
            'marcaje_2': str,
            'marcaje_3': str,
            'horas_previstas': str,
            'horas_normales': str,
            'presencia_real': str,
            'asuntos_propios': str,
            'libre_disposicion': str,
            'maternidad_paternidad': str,
            'horas_compensadas': str,
            'consulta_medico': str,
            'asuntos_sindicales': str,
            'licencias': str,
            'baja_enfermedad': str,
            'bajas_accidente': str,
            'huelga': str,
            'vacaciones_disfrutadas': str,
            'permisos_no_retribuidos': str,
            'total_horas_extras': str,
            'horas_extras_dia': str,
            'horas_extra_noche': str,
            'horas_a_compensar': str,
            'penosidad': str,
            'nocturnidad': str,
        }

        data = pd.read_excel(src, na_values='str', dtype=dtype)
        new_columns = list(map(lambda x: unidecode.unidecode(x.replace(" ", "_").replace(".", "").lower()), data.columns))
        data.columns = new_columns
        data['apellidos_'] = data['apellidos_'].str.replace(',','')
        return data

    @staticmethod
    def load_excel_file_with_conversion(src: str) -> pd.DataFrame:
        logger = logging.getLogger('absbw')

        sub = subprocess.call(['ssconvert', src, src+".csv"])

        out_file = open(src+"_1", "w")
        sub = subprocess.call(['sed', 's/González,\"/González\"/g', src + ".csv"], stdout=out_file)
        logger.warning('Fix 1')

        out_file = open(src+"_1b", "w")
        sub = subprocess.call(['sed', 's/Lado,\"/Lado\"/g', src + "_1"], stdout=out_file)
        logger.warning('Fix 1')

        out_file = open(src+"_2", "w")
        sub = subprocess.call(['sed', 's/\"//g', src+"_1b"], stdout=out_file)
        logger.warning('Fix 2')

        out_file = open(src+"_3", "w")
        sub = subprocess.call(['sed', 's/,/\",\"/g', src+"_2"], stdout=out_file)
        logger.warning('Fix 3')

        out_file = open(src+"_4", "w")
        sub = subprocess.call(['sed', 's/^/\"/g', src+"_3"], stdout=out_file)
        logger.warning('Fix 4')

        out_file = open(src+"_5", "w")
        sub = subprocess.call(['sed', 's/$/\"/g', src+"_4"], stdout=out_file)
        logger.warning('Fix 5')

        out_file = open(src + "_6", "w")
        sub = subprocess.call(['sed', '-r', 's/\"[-  ]*\"|//g', src + "_5"], stdout=out_file)
        logger.warning('Fix 6')


        logger.warning('reading Excel')
        data = pd.read_csv(src+"_6", low_memory=False)

        new_columns = list(map(lambda x: unidecode.unidecode(x.replace(" ", "_").replace(".", "").lower()),
                               data.columns))

        data.columns = new_columns

        os.remove(src + ".csv")
        os.remove(src + "_1")
        os.remove(src + "_1b")
        os.remove(src + "_2")
        os.remove(src + "_3")
        os.remove(src + "_4")
        os.remove(src + "_5")
        os.remove(src + "_6")
        
        return data