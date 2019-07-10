import os

import pandas as pd
import pytest


class TestIntegrationRatings(object):
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
