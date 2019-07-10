from botdetector.services.TwitterProfileInfoRetriever import *


class TestTwitterProfileInfoRetriever(object):
    def test_can_obtain_user_page(self):
        page = obteinUserProfilePage('diegoreico')

        assert len(page) > 0
        assert page.__contains__('@diegoreico')

    def test_obtain_number_of_followers(self):
        page = obteinUserProfilePage('diegoreico')
        tweets = obtain_number_of_tweets(page)

        assert tweets > 100

    def test_tweepy_obtains_user_profile(self):
        result = obtain_user_info('@diegoreico')

        print(result)

        assert(result)