import asyncio
from twikit import Client, TooManyRequests
from datetime import datetime
import csv
from configparser import ConfigParser
from random import randint

MINIMUM_TWEETS = 1000
# queries to use
# QUERY = '"dosen asn" (kemdiktisaintek OR kemendiktisaintek OR mendiktisaintek OR tukin) lang:id until:2025-02-08 since:2024-12-01'
# QUERY = 'tukin lang:id until:2025-02-09 since:2024-12-01'
# QUERY = 'tukin dosen lang:id until:2025-02-09 since:2024-12-01'
# QUERY = 'tunjangan kinerja dosen asn lang:id until:2025-02-09 since:2024-12-01'
# QUERY = 'kemendiktisaintek lang:id until:2025-02-09 since:2024-12-01'
# QUERY = 'dosen lang:id until:2025-02-09 since:2024-12-01'
QUERY = '(from:tukin_dosenASN)'
QUERY = ''
CSV_FILE = 'tweets7.csv'

async def get_tweets(tweets):
    if tweets is None:
        print(f'{datetime.now()} - Getting initial tweets...')
        tweets = await client.search_tweet(QUERY, product='Top')
    else:
        wait_time = randint(7, 15)
        print(f'{datetime.now()} - Getting next tweets after {wait_time} seconds ...')
        await asyncio.sleep(wait_time)
        tweets = await tweets.next()
    return tweets

async def main():
    config = ConfigParser()
    config.read('config.ini')
    username = config['X']['username']
    email = config['X']['email']
    password = config['X']['password']

    with open(CSV_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'created_at', 'user', 'location', 'text', 'in_reply_to', 'reply_count', 'favorite_count', 'hashtags'])

    global client
    client = Client(language='en-US')
    client.load_cookies('cookies1.json')

    tweet_count = 0
    tweets = None

    while tweet_count < MINIMUM_TWEETS:
        try:
            tweets = await get_tweets(tweets)
        except TooManyRequests as e:
            rate_limit_reset = datetime.fromtimestamp(e.rate_limit_reset)
            print(f'{datetime.now()} - Rate limit reached. Waiting until {rate_limit_reset}')
            wait_time = (rate_limit_reset - datetime.now()).total_seconds()
            await asyncio.sleep(wait_time)
            continue

        if not tweets:
            print(f'{datetime.now()} - No more tweets found')
            break

        for tweet in tweets:
            tweet_count += 1
            tweet_data = [
                tweet.id, tweet.created_at_datetime, tweet.user.name, tweet.user.location,
                tweet.text, tweet.in_reply_to, tweet.reply_count, tweet.favorite_count, tweet.hashtags
            ]
            
            with open(CSV_FILE, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(tweet_data)


        print(f'{datetime.now()} - Got {tweet_count} tweets')
        # wait_proceed = randint(3, 7)
        # await asyncio.sleep(wait_proceed)

    print(f'{datetime.now()} - Done! Got {tweet_count} tweets')

if __name__ == "__main__":
    asyncio.run(main())
