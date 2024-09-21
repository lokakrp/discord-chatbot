import discord
from discord.ext import commands
import configparser
import asyncio
import ai
from datetime import datetime
import os
import json

# reads token and API key
config = configparser.ConfigParser()
config.read('token.ini')
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
    if os.path.exists('userdata.json'):
        with open('userdata.json', 'r') as f:
            return json.load(f)
    return {"users": {}}

# Save user data to JSON
def save_user_data(user_data):
    with open('userdata.json', 'w') as f:
        json.dump(user_data, f, indent=4)

user_data = load_user_data()

# Load DJ module
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
        response = await ai_chatbot.get_cohere_response(message.author.id, message.content)
        await message.channel.send(response)
        return

    if bot.user in message.mentions or "nano" in message.content.lower():
        response = await ai_chatbot.get_cohere_response(message.author.id, message.content)
        await message.channel.send(response)

    await bot.process_commands(message)

# Slash command to refresh short-term memory
@bot.tree.command(name="wack", description="refresh the bot's short-term memory")
async def wack(interaction: discord.Interaction):
    await ai_chatbot.refresh_knowledge()
    await interaction.response.send_message("ow that hurts!!", ephemeral=True)

# Slash command to teach the bot something new
@bot.tree.command(name="learn", description="teach the bot new information")
async def learn(interaction: discord.Interaction, *, new_info: str):
    await ai_chatbot.learn_personal_lesson(new_info)
    await interaction.response.send_message(f"i just learned something new: {new_info}", ephemeral=True)

@bot.command()
async def learnfact(ctx, *, fact: str):
    await ai_chatbot.learn_general_fact(fact)
    await ctx.send(f"learned fact: {fact}")

@bot.command()
async def setbirthday(ctx, birthday: str):
    try:
        datetime.strptime(birthday, "%Y-%m-%d")  # Validate date format
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

@bot.command()
async def addfact(ctx, *, fact: str):
    user_id = str(ctx.author.id)
    
    if user_id not in user_data["users"]:
        await ctx.send("you need to set your birthday first")
        return
    
    user_data["users"][user_id]["facts"].append(fact)
    save_user_data(user_data)
    await ctx.send(f"added fact: {fact}")

# Run the bot
async def main():
    async with bot:
        await bot.start(TOKEN)

asyncio.run(main())
