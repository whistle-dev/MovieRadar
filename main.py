import os
import json
import time
import discord
from discord.ext import tasks, commands
from scraper import scrape
from dotenv import load_dotenv
from discord import app_commands
from datetime import datetime, timezone
from notifications import send_to_channel

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
APPLICATION_ID = os.getenv("APPLICATION_ID")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

command_timestamps = {}
server_settings = {}
monitoring_tasks = {}
last_update_timestamps = {}


def load_server_settings():
    global server_settings
    if os.path.exists("server_settings.json"):
        with open("server_settings.json", "r") as f:
            server_settings = json.load(f)
    else:
        server_settings = {}
        save_server_settings()


def save_server_settings():
    with open("server_settings.json", "w") as f:
        json.dump(server_settings, f)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    load_server_settings()
    for guild_id, settings in server_settings.items():
        if settings.get("monitoring", False):
            await start_monitoring(int(guild_id))
    await bot.tree.sync()
    print("Commands synced")


async def monitor_trending(guild_id):
    guild_id = str(guild_id)
    if guild_id in server_settings and server_settings[guild_id]["channel_id"]:
        new_movies = scrape()
        if new_movies:
            await send_to_channel(
                new_movies,
                bot,
                server_settings[guild_id]["channel_id"],
            )
            last_update_timestamps[guild_id] = datetime.now(timezone.utc)


async def start_monitoring(guild_id):
    if guild_id not in monitoring_tasks:
        loop = tasks.loop(seconds=3600)(monitor_trending)
        monitoring_tasks[guild_id] = loop
        loop.start(guild_id)


def stop_monitoring(guild_id):
    if guild_id in monitoring_tasks:
        monitoring_tasks[guild_id].cancel()
        del monitoring_tasks[guild_id]


@bot.tree.command(
    name="setchannel", description="Sets the channel for movie notifications."
)
async def setchannel(interaction: discord.Interaction):
    guild_id = str(interaction.guild_id)
    if interaction.user.guild_permissions.administrator:
        server_settings[guild_id] = {
            "channel_id": interaction.channel_id,
            "monitoring": server_settings.get(guild_id, {}).get("monitoring", False),
        }
        save_server_settings()
        await interaction.response.send_message(
            f"Channel set for movie notifications to <#{interaction.channel_id}>.",
            ephemeral=True,
        )
    else:
        await interaction.response.send_message(
            "You do not have permission to use this command.", ephemeral=True
        )


@bot.tree.command(
    name="trending", description="Fetches and sends the list of trending movies."
)
async def trending(interaction: discord.Interaction):
    guild_id = str(interaction.guild_id)
    current_timestamp = time.time()
    if interaction.user.id in command_timestamps:
        last_timestamp = command_timestamps[interaction.user.id]
        remaining_time = 120 - (current_timestamp - last_timestamp)
        if remaining_time > 0:
            await interaction.response.send_message(
                f"Please wait for {int(remaining_time)} seconds before using this command again.",
                ephemeral=True,
            )
            return
    command_timestamps[interaction.user.id] = current_timestamp
    new_movies = scrape()
    await interaction.response.send_message(
        "Fetching trending movies...", ephemeral=True
    )
    await send_to_channel(
        new_movies,
        bot,
        interaction.channel_id,
    )


@bot.tree.command(
    name="status", description="Displays the current settings for the server."
)
async def status(interaction: discord.Interaction):
    guild_id = str(interaction.guild_id)
    settings = server_settings.get(guild_id, {})
    channel_id = settings.get("channel_id", "Not set")
    channel_mention = f"<#{channel_id}>" if channel_id != "Not set" else "Not set"
    monitoring = "Active" if settings.get("monitoring", False) else "Inactive"
    interval = 60  # Interval is now fixed at 60 minutes
    last_update = last_update_timestamps.get(guild_id, None)
    last_update_str = (
        last_update.strftime("%Y-%m-%d %H:%M:%S") if last_update else "Never"
    )
    hours_ago = (
        ((datetime.now(timezone.utc) - last_update).total_seconds() // 3600)
        if last_update
        else "N/A"
    )

    embed = discord.Embed(
        title="Server Settings",
        color=discord.Color.red(),
    )
    embed.add_field(name="Channel", value=channel_mention, inline=True)
    embed.add_field(name="Monitoring", value=monitoring, inline=True)
    embed.add_field(name="Interval", value=f"{interval} minutes", inline=True)
    embed.add_field(
        name="Last Update",
        value=f"{last_update_str} ({hours_ago} hours ago)",
        inline=True,
    )

    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="ping", description="Check if the bot is live.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!", ephemeral=True)


@bot.tree.command(
    name="startmonitoring", description="Starts monitoring for new movies."
)
async def startmonitoring(interaction: discord.Interaction):
    guild_id = str(interaction.guild_id)
    if interaction.user.guild_permissions.administrator:
        if server_settings[guild_id].get("monitoring", False):
            channel_id = server_settings[guild_id]["channel_id"]
            await interaction.response.send_message(
                f"Already monitoring for new movies and publishing to <#{channel_id}>.",
                ephemeral=True,
            )
        else:
            server_settings[guild_id]["monitoring"] = True
            save_server_settings()
            await start_monitoring(int(guild_id))
            await interaction.response.send_message(
                "Started monitoring for new movies.", ephemeral=True
            )
    else:
        await interaction.response.send_message(
            "You do not have permission to use this command.", ephemeral=True
        )


@bot.tree.command(name="stopmonitoring", description="Stops monitoring for new movies.")
async def stopmonitoring(interaction: discord.Interaction):
    guild_id = str(interaction.guild_id)
    if interaction.user.guild_permissions.administrator:
        server_settings[guild_id]["monitoring"] = False
        save_server_settings()
        stop_monitoring(guild_id)
        await interaction.response.send_message(
            "Stopped monitoring for new movies.", ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "You do not have permission to use this command.", ephemeral=True
        )


bot.run(BOT_TOKEN)
