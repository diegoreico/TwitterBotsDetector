import pandas as pd

class FileService:

    def obtai_userid_from_labeled_file(self, file:str) -> pd.Series:

        data = pd.read_csv(file, sep='\t', names=['id', 'type'])
        ids_to_retrieve = data['id']

        return ids_to_retrieve