import os

import pandas as pd
import pytest

from ars.config import data_table_config as config
from ars.data_sources import Ratings


class TestIntegrationRatings(object):
    @pytest.fixture
    def clear_export_path(self):
        yield  # execute after the test
        items_export_path = config.items_export_path()
        if os.path.isfile(items_export_path):
            os.remove(items_export_path)

    def test_ratings_are_fetched_from_database(self):
        ratings_ds = Ratings()
        ratings_ds.connect()

        ratings = ratings_ds.get_all()

        assert (ratings is not None)
        assert (ratings.size > 0)

    def test_ratings_are_fetched_from_database_and_transformed_into_a_matrix_format(self):
        ratings_ds = Ratings()
        ratings_ds.connect()

        ratings = ratings_ds.get_all()
        ratings_matrix = ratings_ds.get_all_as_matrix()

        num_users = len(ratings[config.user_review_users_column()].unique())
        num_items = len(ratings[config.user_review_items_column()].unique())

        assert (ratings is not None)
        assert (ratings_matrix is not None)
        assert (ratings_matrix.shape[0] == num_users)
        assert (ratings_matrix.shape[1] == num_items)

    @pytest.mark.usefixtures('clear_export_path')
    def test_ratings_are_exported_to_csv(self):
        ratings_ds = Ratings()
        ratings_ds.connect()

        ratings = ratings_ds.get_all()
        ratings_ds.export_items()

        items = pd.read_csv(config.items_export_path())
        num_items = len(ratings[config.user_review_items_column()].unique())

        assert (items is not None)
        assert (items.shape == (num_items, 1))
