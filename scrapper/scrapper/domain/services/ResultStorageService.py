import datetime
import pandas as pd

from pathlib import Path
from scrapper.configuration import config


class ResultStorageService:

    def __init__(self):
        self._timestamp = datetime.datetime.now().timestamp()

    def store_user_profiles(self, profiles: pd.DataFrame) -> None:
        # creates folder
        folder_profiles = config.Folders.OUTPUT_DIR_PROFILES
        Path(folder_profiles).mkdir(parents=True, exist_ok=True)

        # builds file path
        dataframe_profile_path = (folder_profiles / str(self._timestamp))
        dataframe_profile_path = dataframe_profile_path\
            .with_suffix(dataframe_profile_path.suffix + '.csv')

        # stores file
        profiles.to_csv(dataframe_profile_path)

    def store_tweets(self, tweets: pd.DataFrame) -> None:
        # creates folder
        folder_timelines = config.Folders.OUTPUT_DIR_TIMELINES
        Path(folder_timelines).mkdir(parents=True, exist_ok=True)

        # build file path
        dataframe_timeline_path = (folder_timelines / str(self._timestamp))
        dataframe_timeline_path = dataframe_timeline_path\
            .with_suffix(dataframe_timeline_path.suffix + '.csv')

        # store file
        tweets.to_csv(dataframe_timeline_path)
