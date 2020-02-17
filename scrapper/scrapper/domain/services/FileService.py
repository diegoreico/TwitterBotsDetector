import pandas as pd
from pathlib import Path

class FileService:

    def obtain_userid_from_labeled_file(self, file:str) -> pd.Series:

        data = pd.read_csv(file, sep='\t', names=['id', 'type'])
        ids_to_retrieve = data['id']

        return ids_to_retrieve

    def extract_file_name(self, file:str) -> str:
        path = Path(file)
        filename = path.name.split(".")[0]
        return filename