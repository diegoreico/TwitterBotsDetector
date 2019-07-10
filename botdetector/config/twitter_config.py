import os


# DATABASE CONFIGURATION
def twitter_api_key() -> str:
    return os.getenv('TWITTER_API_KEY')


def twitter_api_key_secret() -> str:
    return os.getenv('TWITTER_API_KEY_SECRET')


def twitter_access_token() -> str:
    return os.getenv('TWITTER_ACCESS_TOKEN')


def twitter_access_token_secret() -> str:
    return os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

