import discord
import requests
import asyncio
from bs4 import BeautifulSoup
import os

TOKEN = 'TOKEN'  # Replace with your bot token
CHANNEL_ID = 'CHANNEL ID'  # Replace with your channel ID
AO3_URL = 'URL'  # Replace with your AO3 fanfiction URL
LAST_UPDATED_FILE = 'last_updated.txt'  # File to store the last updated value

# Define the intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

client = discord.Client(intents=intents)

def check_for_updates():
    response = requests.get(AO3_URL)
    soup = BeautifulSoup(response.content, 'html.parser')
    element = soup.select_one('dd.status')
    if element:
        last_updated = element.text.strip()
    else:
        last_updated = None
    return last_updated

def read_last_updated():
    if os.path.exists(LAST_UPDATED_FILE):
        try:
            with open(LAST_UPDATED_FILE, 'r') as file:
                return file.read().strip()
        except Exception as e:
            print(f"Error reading {LAST_UPDATED_FILE}: {e}")
    return None

def write_last_updated(last_updated):
    try:
        with open(LAST_UPDATED_FILE, 'w') as file:
            file.write(last_updated)
    except Exception as e:
        print(f"Error writing to {LAST_UPDATED_FILE}: {e}")

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    channel = client.get_channel(int(CHANNEL_ID))
    if channel is None:
        print(f'Channel with ID {CHANNEL_ID} not found')
        return

    last_updated = read_last_updated()
    if last_updated is None:
        print('No last updated information found, starting fresh.')

    while True:
        current_updated = check_for_updates()
        if current_updated is None:
            print('Failed to find the update element on the page')
        elif last_updated is None:
            last_updated = current_updated
            write_last_updated(last_updated)
        elif current_updated != last_updated:
            await channel.send(f'The fanfiction has been updated! Check it out here: {AO3_URL}')
            last_updated = current_updated
            write_last_updated(last_updated)

        await asyncio.sleep(3600)  # Check every hour

client.run(TOKEN)
