from botdetector.config import data_table_config as config
from botdetector.data_sources import Ratings
from botdetector.tests.utils import load_ratings_from_file


class TestUnitRatings(object):
    def test_transform_ratings_db_into_matrix_format(self, mocker):
        ratings_ds = Ratings()
        mocker.patch.object(ratings_ds, 'get_all')
        ratings_ds.get_all.return_value = load_ratings_from_file()
        
        ratings = ratings_ds.get_all()
        ratings_matrix = ratings_ds.get_all_as_matrix()
        
        num_users = len(ratings[config.user_review_users_column()].unique())
        num_items = len(ratings[config.user_review_items_column()].unique())
        
        assert (ratings_matrix is not None)
        assert (ratings_matrix.shape[0] == num_users)
        assert (ratings_matrix.shape[1] == num_items)
