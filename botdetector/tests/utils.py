import os

import numpy as np
import pandas as pd

from ars.config import data_table_config as config


def load_ratings_from_file() -> pd.DataFrame:
    file_path = os.path.join("data/processed/UserReview.csv")
    
    data = pd.read_csv(file_path)[['SprintID', 'UserID', 'Rating']]
    data = data.rename(index=str, columns={
        'UserID': config.user_review_users_column(),
        'SprintID': config.user_review_items_column(),
        'Rating': config.user_review_ratings_column()
    })
    
    return data


def get_random_data_frame():
    np.random.randint(0, 5, size=(100, 50))
    return pd.DataFrame(np.random.randint(0, 5, size=(100, 50)))
