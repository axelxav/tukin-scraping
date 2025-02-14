import asyncio
from twikit import Client, TooManyRequests
from datetime import datetime
import csv
from configparser import ConfigParser
from random import randint
import httpx  # For handling connection errors

MINIMUM_TWEETS = 1000
# Queries
# QUERY = '"dosen asn" (kemdiktisaintek OR kemendiktisaintek OR mendiktisaintek OR tukin) lang:id until:2025-02-08 since:2024-12-01'
# QUERY = 'tukin lang:id until:2025-02-09 since:2024-12-01'
# QUERY = 'tukin dosen lang:id until:2025-02-09 since:2024-12-01'
# QUERY = 'tunjangan kinerja dosen asn lang:id until:2025-02-09 since:2024-12-01'
# QUERY = 'kemendiktisaintek lang:id until:2025-02-09 since:2024-12-01'
# QUERY = 'dosen lang:id until:2025-02-09 since:2024-12-01'
# QUERY = 'kemendiktiristek lang:id until:2025-02-09 since:2024-12-01'
# QUERY = 'tukin asn dosen lang:id until:2025-02-09 since:2024-12-01'
# QUERY = 'kesejahteraan dosen lang:id until:2025-02-09 since:2024-12-01'
# QUERY = 'dosen asn lang:id until:2025-02-09 since:2024-12-01'
# QUERY = '(#tukinforall) lang:id until:2025-02-10 since:2024-12-01'
QUERY = '(#bayartukindosenkemdiktisaintek OR #tukinforall OR #dosenbukansapiperah) lang:id until:2025-02-13 since:2025-01-01'
CSV_FILE = './new_tweets/tweets4.csv'

async def get_tweets(tweets):
    """Retrieve tweets asynchronously, handling request limits."""
    try:
        if tweets is None:
            print(f'{datetime.now()} - Getting initial tweets...')
            tweets = await client.search_tweet(QUERY, product='Top')
        else:
            wait_time = randint(15, 30)  # Increased delay to avoid blocks
            print(f'{datetime.now()} - Waiting {wait_time} seconds before the next request...')
            await asyncio.sleep(wait_time)
            tweets = await tweets.next()

        return tweets

    except TooManyRequests as e:
        rate_limit_reset = datetime.fromtimestamp(e.rate_limit_reset)
        wait_time = (rate_limit_reset - datetime.now()).total_seconds()
        print(f'{datetime.now()} - Rate limit reached. Retrying in {int(wait_time)} seconds...')
        await asyncio.sleep(wait_time)
        return None

    except httpx.ConnectTimeout:
        print(f'{datetime.now()} - Connection timeout. Retrying in 60 seconds...')
        await asyncio.sleep(60)
        return None

async def main():
    """Main async function to authenticate and fetch tweets."""
    # Load credentials
    config = ConfigParser()
    config.read('config.ini')

    # Ensure valid credentials exist
    try:
        username = config['X']['username']
        email = config['X']['email']
        password = config['X']['password']
    except KeyError:
        print("❌ Missing credentials in config.ini. Please check the file.")
        return

    # Initialize CSV file
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'created_at', 'user', 'location', 'text', 'in_reply_to', 'reply_count', 'favorite_count', 'hashtags'])

    # Authenticate with X (Twitter)
    global client
    client = Client(language='en-US')
    
    try:
        client.load_cookies('cookies1.json')  # Ensure cookies.json is valid
    except FileNotFoundError:
        print("❌ 'cookies.json' not found! Please login and save cookies first.")
        return

    tweet_count = 0
    tweets = None

    while tweet_count < MINIMUM_TWEETS:
        tweets = await get_tweets(tweets)

        if not tweets:
            print(f'{datetime.now()} - No more tweets found or request failed.')
            break

        for tweet in tweets:
            tweet_count += 1
            tweet_data = [
                tweet.id, tweet.created_at_datetime, tweet.user.name, tweet.user.location,
                tweet.text, tweet.in_reply_to, tweet.reply_count, tweet.favorite_count, tweet.hashtags
            ]
            
            # Append tweet data to CSV
            with open(CSV_FILE, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(tweet_data)

        print(f'{datetime.now()} - Collected {tweet_count} tweets so far...')

    print(f'{datetime.now()} - Done! A total of {tweet_count} tweets were collected.')

if __name__ == "__main__":
    asyncio.run(main())
