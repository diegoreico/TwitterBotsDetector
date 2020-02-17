import logging
import pandas as pd

from scrapper.configuration import config
from scrapper.infraestructure.TwitterScrapper import TwitterScrapper

class TwitteService:

    def __init__(self):
        self._twitter_scrapper = TwitterScrapper()

    def scrap_profiles_from_user_ids(self, user_ids: list) -> list:
        profiles = []
        progress = 0
        total = len(user_ids)
        for user_id in user_ids:
            profile = self._twitter_scrapper.retrieve_user_profile(user_id)
            if profile['id'] > 0:
                profiles.append(profile)

            progress += 1
            if progress % 10 == 0:
                logging.debug(f'Current progress retrieving profiles:'
                              f' {progress/total}')

        return profiles

    def scrap_tweets_from_users_timelines(self,
                  user_ids: list,
                  tweets_to_retrieve: int = config.tweets_retrieve_per_timeline
                                          ) -> list:
        tweets = []
        progress = 0
        total = len(user_ids)
        # retrieve user timelines
        for user_id in user_ids:
            user_timeline = self \
                    ._twitter_scrapper \
                    .retrieve_user_timeline(user_id, tweets_to_retrieve)

            for tweet in user_timeline:
                if tweet['id'] > 0:
                    tweets.append(tweet)

            progress += 1
            if progress % 10 == 0:
                logging.debug(f'Current progress retrieving user timelines:'
                              f' {progress / total}')

        return tweets