import asyncio  # Import asyncio for running async functions
from twikit import Client, TooManyRequests
import time
from datetime import datetime
import csv
from configparser import ConfigParser
from random import randint

MINIMUM_TWEETS = 100
QUERY = 'tukin'

# login credentials
config = ConfigParser()
config.read('config.ini')
username = config['X']['username']
email = config['X']['email']
password = config['X']['password']

client = Client(language='en-US')

# authenticate to X.com
# async def login():
#     await client.login(auth_info_1=username, auth_info_2=email, password=password)
#     client.save_cookies('cookies.json')

# # Run the async main function
# asyncio.run(login())

# using the cookies
client.load_cookies('cookies.json')

# get tweets
tweet_count = 0
tweets = None

while tweet_count < MINIMUM_TWEETS:
    if tweets is None:
        # get first tweet
        print(f'{datetime.now()} - Getting first tweet')
        tweets = client.search_tweets(QUERY, 'Latest')
    else:
        print(f'{datetime.now()} - Getting next tweets')
        tweets = tweets.next()
    
    for tweet in tweets:
        tweet_count += 1
        print(f'{datetime.now()} - {tweet_count}. {tweet}')
        with open('tweets.csv', mode='a') as f:
            writer = csv.writer(f)
            writer.writerow([tweet])