import requests
from dotenv import load_dotenv
import os
import time

load_dotenv()

APPLICATION_ID = os.getenv("APPLICATION_ID")
BOT_TOKEN = os.getenv("BOT_TOKEN")

headers = {"Authorization": f"Bot {BOT_TOKEN}"}

# Define commands
commands = [
    {
        "name": "setchannel",
        "description": "Sets the channel for movie notifications.",
        "type": 1,
    },
    {
        "name": "trending",
        "description": "Fetches and sends the list of trending movies.",
        "type": 1,
    },
    {
        "name": "status",
        "description": "Displays the current settings for the server.",
        "type": 1,
    },
    {
        "name": "ping",
        "description": "Check if the bot is live.",
        "type": 1,
    },
    {
        "name": "startmonitoring",
        "description": "Starts monitoring for new movies.",
        "type": 1,
    },
    {
        "name": "stopmonitoring",
        "description": "Stops monitoring for new movies.",
        "type": 1,
    },
]

# Register global commands with a delay to handle rate limits
for command in commands:
    response = requests.post(
        f"https://discord.com/api/v10/applications/{APPLICATION_ID}/commands",
        headers=headers,
        json=command,
    )
    print(response.json())
    time.sleep(2)  # Delay to handle rate limits
