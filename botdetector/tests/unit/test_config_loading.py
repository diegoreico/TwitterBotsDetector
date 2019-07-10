from botdetector.config.twitter_config import *

class TestTwitterProfileInfoRetriever(object):
    def test_can_obtain_twitter_api_tokens(self):
        print(twitter_access_token())
        assert(twitter_access_token() == 'test')
        assert(twitter_access_token_secret() == 'test')
        assert(twitter_api_key() == 'test')
        assert(twitter_api_key_secret() == 'test')