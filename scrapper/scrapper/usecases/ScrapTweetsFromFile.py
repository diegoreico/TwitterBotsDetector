import logging
import pandas as pd

from scrapper.usecases.base import BaseUseCase
from scrapper.domain.services.FileService import FileService
from scrapper.domain.services.TwitterService import TwitteService
from scrapper.domain.services.ResultStorageService import ResultStorageService

class ScrapTweetsFromFile(BaseUseCase):

    def __init__(self, file):
        super().__init__()
        self._file = file        

    def execute(self):
        logging.info('executing ScrapTweetsFromFile use case')

        file_service = FileService()
        twitter_service = TwitteService()
        result_storage = ResultStorageService()

        ids_to_retrieve = file_service.obtai_userid_from_labeled_file(self._file)
        profiles = twitter_service.scrap_profiles_from_user_ids(ids_to_retrieve)
        profiles = pd.DataFrame(profiles, columns=profiles[0].keys())
        result_storage.store_user_profiles(profiles)

        tweets = twitter_service.scrap_tweets_from_users_timelines(ids_to_retrieve)
        tweets = pd.DataFrame(tweets, columns=tweets[0].keys())
        result_storage.store_tweets(tweets)

