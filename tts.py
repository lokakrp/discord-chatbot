import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from gtts import gTTS
import os

class TTS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def play_tts(self, channel, text):
        voice_client = await channel.connect()

        try:
            # Create TTS audio file from the text and save it in __pycache__
            pycache_dir = os.path.join(os.path.dirname(__file__), '__pycache__')
            os.makedirs(pycache_dir, exist_ok=True)
            audio_file = os.path.join(pycache_dir, "tts_output.mp3")

            tts = gTTS(text)
            tts.save(audio_file)

            # Play the audio file in the voice channel
            voice_client.play(discord.FFmpegPCMAudio(audio_file), after=lambda e: print(f'Finished playing: {e}'))
            while voice_client.is_playing():
                await asyncio.sleep(1)

        finally:
            # Disconnect after playing
            if voice_client.is_connected():
                await voice_client.disconnect()

            # Clean up: remove the audio file after it's played
            if os.path.exists(audio_file):
                os.remove(audio_file)

    @app_commands.command(name="tts", description="Converts text to speech and plays it in VC")
    async def tts(self, interaction: discord.Interaction, text: str):
        user = interaction.user  # Get the user who ran the command
        print(f"{user.name} played a TTS message: {text}")  # Print the user and message to the terminal

        if not user.voice:
            await interaction.response.send_message("You need to be in a voice channel to use TTS.", ephemeral=True)
            return

        # Acknowledge the command immediately
        await interaction.response.send_message("Playing your message...", ephemeral=True)

        channel = user.voice.channel
        await self.play_tts(channel, text)

# Setup function to load the cog
async def setup(bot):
    await bot.add_cog(TTS(bot))
