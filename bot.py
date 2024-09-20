import discord
from discord.ext import commands
import configparser
import asyncio

# Read token from token.ini
config = configparser.ConfigParser()
config.read('token.ini')
TOKEN = config['discord']['token'].strip()

# Create a bot instance with the commands extension
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True  # Add voice states intent for audio features
bot = commands.Bot(command_prefix='!', intents=intents)

# Load the DJ cog
async def load_extensions():
    await bot.load_extension('dj')  # Ensure correct path to dj.py

# Event when bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user} is now running!')
    await load_extensions()  # Ensure cog is loaded on ready
    await bot.tree.sync()  # Sync slash commands

# Run the bot
async def main():
    async with bot:
        await bot.start(TOKEN)

asyncio.run(main())
