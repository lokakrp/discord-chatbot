import discord
from discord.ext import commands
import configparser
import asyncio
import ai  # Import your AIChatbot class

# Read token and API key from token.ini
config = configparser.ConfigParser()
config.read('token.ini')
TOKEN = config['discord']['token'].strip()
COHERE_API_KEY = config['cohere']['api_key'].strip()

# Initialize the bot with necessary intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Initialize Cohere AI Chatbot with the API key from token.ini
ai_chatbot = ai.AIChatbot(api_key=COHERE_API_KEY)

# Load the DJ cog for music commands
async def load_extensions():
    await bot.load_extension('dj')

@bot.event
async def on_ready():
    print(f'{bot.user} is now running!')
    await load_extensions()
    await bot.tree.sync()

@bot.event
async def on_message(message):
    if message.author == bot.user or message.mention_everyone:
        return

    if isinstance(message.channel, discord.DMChannel):
        response = await ai_chatbot.get_cohere_response(message.content)
        await message.channel.send(response)
        return

    if bot.user in message.mentions or "nano" in message.content.lower():
        response = await ai_chatbot.get_cohere_response(message.content)
        await message.channel.send(response)

    await bot.process_commands(message)

# Slash command to refresh short-term memory
@bot.tree.command(name="wack", description="refresh the bots short term memory")
async def wack(interaction: discord.Interaction):
    await ai_chatbot.refresh_knowledge()
    await interaction.response.send_message("ow that hurts!!", ephemeral=True)

# Slash command to teach the bot something new
@bot.tree.command(name="learn", description="teach the bot new information")
async def learn(interaction: discord.Interaction, *, new_info: str):
    await ai_chatbot.learn(new_info)
    await interaction.response.send_message(f"i just learned something new: {new_info}", ephemeral=True)

# Run the bot
async def main():
    async with bot:
        await bot.start(TOKEN)

asyncio.run(main())
