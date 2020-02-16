
import logging
import requests
import tweepy

from tweepy.error import TweepError

from scrapper.configuration.config import TwitterConfig

class TwitterScrapper():

    def __init__(self):
        self._auth = tweepy.OAuthHandler(TwitterConfig.CONSUMER_KEY, TwitterConfig.CONSUMER_SECRET)
        self._auth.set_access_token(TwitterConfig.ACCESS_TOKEN, TwitterConfig.ACCESS_TOKEN_SECRET)
        self._api = tweepy.API(self._auth)
        

    def retrieve_user_profile(self, user: int) -> dict:
        logging.info(f'retrieving user profile: {user}')

        try:
            twitteruser = self._api.lookup_users(user_ids=[user])[0]._json
        except TweepError as error:
            logging.error(error)
            twitteruser = {'id': -user, 'code': error.api_code,'message': error.reason}
        
        return twitteruser
        

    def retrieve_user_timeline(self, user: int, number_of_tweets: int) -> dict:
        logging.info(f'retrieving tweets for user: {user}')

        try:
            public_tweets = self._api.user_timeline(user_id=int(user), count=number_of_tweets)
            result = [tweet._json for tweet in public_tweets]
        except TweepError as error:
            logging.error(error)
            result = [{'id': -user, 'code': error.api_code,'message': error.reason}]

        return result