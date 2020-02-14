import logging
import itertools
import os
import datetime
import pandas as pd

from pathlib import Path

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

        profiles = []
        progress = 0
        total = len(ids_to_retrieve)
        for user_id in ids_to_retrieve:
            profile = twitter_scrapper.retrieve_user_profile(user_id)
            if profile['id'] > 0:
                profiles.append(profile)

            progress += 1
            if progress % 10 == 0:
                logging.debug(f'Current progress retrieving profiles: {progress/total}')

        ts = datetime.datetime.now().timestamp()

        folder_profiles = config.Folders.OUTPUT_DIR_PROFILES
        Path(folder_profiles).mkdir(parents=True, exist_ok=True)
        dataframe_profile_path = (folder_profiles / str(ts))
        dataframe_profile_path = dataframe_profile_path.with_suffix(dataframe_profile_path.suffix + '.csv')
        data_profile_df = pd.DataFrame(profiles, columns=profiles[0].keys())
        data_profile_df.to_csv(dataframe_profile_path)


        tweets=[]
        progress = 0
        # retrieve user timelines
        for user_id in ids_to_retrieve:
            user_timeline = twitter_scrapper.retrieve_user_timeline(user_id, config.tweets_retrieve_per_timeline)
            for tweet in user_timeline:
                if tweet['id'] > 0:
                    tweets.append(tweet)

            progress += 1
            if progress % 10 == 0:
                logging.debug(f'Current progress retrieving user timelines: {progress/total}')

        folder_timelines = config.Folders.OUTPUT_DIR_TIMELINES
        Path(folder_timelines).mkdir(parents=True, exist_ok=True)
        dataframe_timeline_path = (folder_timelines / str(ts))
        dataframe_timeline_path = dataframe_timeline_path.with_suffix(dataframe_timeline_path.suffix + '.csv')
        data_timeline_df = pd.DataFrame(tweets, columns=tweets[0].keys())
        data_timeline_df.to_csv(dataframe_timeline_path)

