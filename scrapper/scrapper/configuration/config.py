import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv('.env')

class TwitterConfig:
    CONSUMER_KEY=os.getenv('CONSUMER_KEY')
    CONSUMER_SECRET=os.getenv('CONSUMER_SECRET')
    ACCESS_TOKEN=os.getenv('ACCESS_TOKEN')
    ACCESS_TOKEN_SECRET=os.getenv('ACCESS_TOKEN_SECRET')

class Folders:
    OUTPUT_DIR=Path(os.getenv('OUTPUT_DIR'))
    OUTPUT_DIR_PROFILES=OUTPUT_DIR / os.getenv('OUTPUT_DIR_PROFILES')
    OUTPUT_DIR_TIMELINES=OUTPUT_DIR / os.getenv('OUTPUT_DIR_TIMELINES')

tweets_retrieve_per_timeline = os.getenv('TWEETS_TO_RETRIEVE_PER_TIMELINE')