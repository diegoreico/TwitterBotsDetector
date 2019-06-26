from typing import List, Tuple

import numpy as np
import pandas as pd

from ars.config import data_table_config as config
from ars.data_sources.data_source import DataSource
from ars.utils import check_file_path


class Ratings(DataSource):
    def __init__(self):
        super().__init__()

        self.__ratings_table = config.user_review_table_name()
        self.__users_column = config.user_review_users_column()
        self.__items_column = config.user_review_items_column()
        self.__ratings_column = config.user_review_ratings_column()

    def get_all(self) -> pd.DataFrame:
        query = "SELECT {}, {}, {} FROM {}".format(self.__users_column, self.__items_column, self.__ratings_column,
                                                   self.__ratings_table)
        self.cursor.execute(query)
        ratings_tuples: List[Tuple] = list(self.cursor.fetchall())

        return pd.DataFrame(ratings_tuples, columns=[self.__users_column, self.__items_column, self.__ratings_column])

    def get_all_as_matrix(self) -> pd.DataFrame:
        return pd.pivot_table(self.get_all(),
                              values=self.__ratings_column,
                              index=self.__users_column,
                              columns=self.__items_column).fillna(0)

    def export_items(self):
        export_path = config.items_export_path()
        check_file_path(export_path)

        item_values = np.sort(self.get_all_as_matrix().columns.values)
        pd.DataFrame.from_dict({'items': item_values}).to_csv(export_path, index=False)
