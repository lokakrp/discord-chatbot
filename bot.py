import discord
from discord.ext import commands
import responses
import configparser

# Read token from token.ini
config = configparser.ConfigParser()
config.read('token.ini')
TOKEN = config['discord']['token'].strip()

# Create a bot instance with the commands extension
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='?', intents=intents)

# Load the DJ cog
async def load_extensions():
    await bot.load_extension('dj')

@bot.event
async def on_ready():
    print(f'{bot.user} is now running!')
    await load_extensions()  # Load the DJ cog

# Handle messages
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    username = str(message.author)
    user_message = str(message.content)
    channel = str(message.channel)

    print(f'{username} said: "{user_message}" ({channel})')

    if user_message.startswith("?"):
        user_message = user_message[1:]
        await send_message(message, user_message, is_private=True)
    else:
        await send_message(message, user_message, is_private=False)

# Send messages with response handling
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
bot.run(TOKEN)
