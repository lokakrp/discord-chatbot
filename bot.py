import discord
from discord.ext import commands
import configparser
import asyncio
import ai
from datetime import datetime
import os
import json

# Paths to files (made compatible for Linux)
DATA_FOLDER = 'data'
TOKEN_FILE = os.path.join(DATA_FOLDER, 'token.ini')
USERDATA_FILE = os.path.join(DATA_FOLDER, 'userdata.json')
KNOWLEDGE_FILE = os.path.join(DATA_FOLDER, 'knowledge.json')

# Reads token and API key from token.ini
config = configparser.ConfigParser()
config.read(TOKEN_FILE)
TOKEN = config['discord']['token'].strip()
COHERE_API_KEY = config['cohere']['api_key'].strip()

# Initialize bot intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Initialize chatbot
ai_chatbot = ai.AIChatbot(api_key=COHERE_API_KEY)

# Load user data from JSON
def load_user_data():
    if os.path.exists(USERDATA_FILE):
        with open(USERDATA_FILE, 'r') as f:
            return json.load(f)
    return {"users": {}}

# Save user data to JSON
def save_user_data(user_data):
    with open(USERDATA_FILE, 'w') as f:
        json.dump(user_data, f, indent=4)

user_data = load_user_data()

# Load modules
async def load_extensions():
    await bot.load_extension('dj')
    await bot.load_extension('tts')
    await bot.load_extension('converter')  # Ensure 'converter.py' file is in the same directory

@bot.event
async def on_ready():
    print(f'{bot.user} is now running!')
    await load_extensions()  # Load extensions when the bot is ready
    await bot.tree.sync()  # Sync slash commands
    print("Commands have been synced.")

# Respond to users
@bot.event
async def on_message(message):
    user_id = str(message.author.id)

    # Check if the user is in the auto-delete list
    if user_id in user_data["users"] and user_data["users"][user_id].get("auto_delete"):
        await message.delete()
        return

    if isinstance(message.channel, discord.DMChannel):
        response = await ai_chatbot.get_cohere_response(message.author.id, message.content)
        await message.channel.send(response)
        return

    if bot.user in message.mentions or "nano" in message.content.lower():
        response = await ai_chatbot.get_cohere_response(message.author.id, message.content)
        await message.channel.send(response)

    await bot.process_commands(message)

# Refresh short-term memory
@bot.tree.command(name="wack", description="refresh the bot's short-term memory")
async def wack(interaction: discord.Interaction):
    await ai_chatbot.refresh_knowledge()
    await interaction.response.send_message("ow that hurts!!", ephemeral=True)

# Teach the bot something new
@bot.tree.command(name="learn", description="teach the bot new information")
async def learn(interaction: discord.Interaction, *, new_info: str):
    await ai_chatbot.learn_personal_lesson(new_info)
    await interaction.response.send_message(f"i just learned something new: {new_info}", ephemeral=True)

# Add slash command for auto-deleting messages
@bot.tree.command(name="autodelete", description="automatically delete a user's messages")
@commands.has_permissions(administrator=True)
async def autodelete(interaction: discord.Interaction, user: discord.User):
    user_id = str(user.id)

    # Add user to auto-delete list in user data
    if user_id not in user_data["users"]:
        user_data["users"][user_id] = {
            "auto_delete": True
        }
    else:
        user_data["users"][user_id]["auto_delete"] = True

    save_user_data(user_data)
    await interaction.response.send_message(f"Auto-deleting messages from {user.name}", ephemeral=True)

# Birthday functions
@bot.command()
async def setbirthday(ctx, birthday: str):
    try:
        datetime.strptime(birthday, "%Y-%m-%d")  
        user_id = str(ctx.author.id)
        user_name = ctx.author.name

        # Update user data
        if user_id not in user_data["users"]:
            user_data["users"][user_id] = {
                "name": user_name,
                "birthday": birthday,
                "facts": [],
                "likes_user": True,
                "attitude": "excited"
            }
        else:
            user_data["users"][user_id]["birthday"] = birthday

        user_data["users"][user_id]["age"] = ai_chatbot.calculate_age(birthday)
        save_user_data(user_data)

        await ctx.send(f"set your birthday to {birthday}")
    except ValueError:
        await ctx.send("please provide your birthday in YYYY-MM-DD format")

# Learn facts
@bot.command()
async def learnfact(ctx, *, fact: str):
    await ai_chatbot.learn_general_fact(fact)
    await ctx.send(f"learned fact: {fact}")

# Run the bot
async def main():
    async with bot:
        await bot.start(TOKEN)

asyncio.run(main())
