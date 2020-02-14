import logging
import itertools
import os

import pandas as pd

from scrapper.usecases.base import BaseUseCase
from scrapper.configuration import config
from scrapper.domain.services.TwitterScrapService import TwitterScrapService

class ScrapTweetsFromFile(BaseUseCase):

    def __init__(self, file):
        super().__init__()
        self._file = file        

    def execute(self):
        logging.info('executing ScrapTweetsFromFile use case')

        data = pd.read_csv(self._file, sep='\t', names=['id','type'])
        ids_to_retrieve = data['id']

        twitter_scrapper = TwitterScrapService()

        profiles = list(map(lambda x: twitter_scrapper.retrieve_user_profile(int(x)), ids_to_retrieve))
        list_of_tweets_per_user = list(map(lambda x: twitter_scrapper.retrieve_user_timeline(x, config.tweets_retrieve_per_timeline), ids_to_retrieve))
        list_of_tweets = list(itertools.chain.from_iterable(list_of_tweets_per_user))

        import datetime;
        ts = datetime.datetime.now().timestamp()

        from pathlib import Path
        folder_profiles = config.Folders.OUTPUT_DIR_PROFILES
        folder_timelines = config.Folders.OUTPUT_DIR_TIMELINES
        Path(folder_profiles).mkdir(parents=True, exist_ok=True)
        Path(folder_timelines).mkdir(parents=True, exist_ok=True)

        dataframe_timeline_path = (folder_timelines / str(ts))
        dataframe_timeline_path = dataframe_timeline_path.with_suffix(dataframe_timeline_path.suffix + '.csv')

        dataframe_profile_path = (folder_profiles / str(ts))
        dataframe_profile_path = dataframe_profile_path.with_suffix(dataframe_profile_path.suffix + '.csv')

        data_timeline_df = pd.DataFrame(list_of_tweets, columns=list_of_tweets[0].keys()).head()
        data_timeline_df.to_csv(dataframe_timeline_path)

        data_profile_df = pd.DataFrame(profiles, columns=profiles[0].keys()).head()
        data_profile_df.to_csv(dataframe_profile_path)
