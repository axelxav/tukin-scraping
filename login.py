import asyncio  # Import asyncio for running async functions
from twikit import Client, TooManyRequests
from configparser import ConfigParser

# login credentials
config = ConfigParser()
config.read('config.ini')
username = config['number2']['username']
email = config['number2']['email']
password = config['number2']['password']

client = Client(language='en-US')

# authenticate to X.com
async def login():
    await client.login(auth_info_1=username, auth_info_2=email, password=password)
    client.save_cookies('cookies1.json')

# Run the async main function
asyncio.run(login())
