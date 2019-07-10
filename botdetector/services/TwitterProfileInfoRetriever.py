import string
import requests

from botdetector.config.twitter_config import *
from bs4 import BeautifulSoup

import tweepy

auth = tweepy.OAuthHandler(twitter_api_key(), twitter_api_key_secret())
auth.set_access_token(twitter_access_token(), twitter_access_token_secret())

api = tweepy.API(auth)


def obteinUserProfilePage(user: string) -> string:
    if user[0] == '@':
        user = user[1:]

    r = requests.get('http://twitter.com/'+user)

    return r.text


def obtain_number_of_tweets(page: string) -> int:
    soup = BeautifulSoup(page, 'html.parser')
    results = soup.find_all('li', class_ = 'ProfileNav-item ProfileNav-item--tweets is-active')[0]
    results = results.find_all('span', class_ = 'ProfileNav-value')[0]

    value = int(results['data-count'])

    return value

def obtain_user_info(user: string):
    return api.get_user(user)


