import discord
from discord.ext import commands
import configparser
import asyncio
import responses

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
    await bot.load_extension('dj')  # This will await the load_extension coroutine

@bot.event
async def on_ready():
    print(f'{bot.user} is now running!')
    await load_extensions()  # Ensure cog is loaded on ready

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    username = str(message.author)
    user_message = str(message.content)
    channel = str(message.channel)

    print(f'{username} said: "{user_message}" ({channel})')

    if isinstance(message.channel, discord.DMChannel):
        # Respond to any message in private messages
        await send_message(message, user_message, is_private=True)
    elif user_message.startswith("!"):
        # Respond to messages starting with '!' in server channels
        user_message = user_message[1:]
        await send_message(message, user_message, is_private=False)

    # Ensure commands are processed
    await bot.process_commands(message)

async def send_message(message, user_message, is_private):
    try:
        response = responses.get_response(user_message)
        if is_private:
            await message.author.send(response)
        else:
            await message.channel.send(response)
    except Exception as e:
        print(e)

# Run the bot
async def main():
    await bot.start(TOKEN)

asyncio.run(main())
