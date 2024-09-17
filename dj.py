import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import tempfile
import os

class DJ(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ytdl_format_options = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'default_search': 'auto',
            'quiet': True,
        }
        self.ffmpeg_options = {
            'options': '-vn'
        }

    @commands.command()
    async def play(self, ctx, url):
        """Play music from a URL (YouTube, SoundCloud, etc.)"""
        if ctx.voice_client is None:
            await ctx.send("I need to be in a voice channel to play music.")
            return

        voice_client = ctx.voice_client

        if 'spotify.com' in url:
            await self.play_spotify(ctx, url)
        elif 'soundcloud.com' in url:
            await self.play_soundcloud(ctx, url)
        else:
            await self.play_from_url(ctx, url)

    async def play_from_url(self, ctx, url):
        """Play music from a regular URL (e.g., YouTube)."""
        voice_client = ctx.voice_client

        with youtube_dl.YoutubeDL(self.ytdl_format_options) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['formats'][0]['url']

        voice_client.stop()
        voice_client.play(discord.FFmpegPCMAudio(url2, **self.ffmpeg_options))
        await ctx.send(f'Now playing: {info["title"]}')

    async def play_spotify(self, ctx, url):
        """Play music from Spotify by downloading and streaming."""
        await self.download_and_play(ctx, url)

    async def play_soundcloud(self, ctx, url):
        """Play music from SoundCloud by downloading and streaming."""
        await self.download_and_play(ctx, url)

    async def download_and_play(self, ctx, url):
        """Download and play music from a URL."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            temp_file_path = temp_file.name

        # Download the track
        with youtube_dl.YoutubeDL({'format': 'bestaudio/best', 'outtmpl': temp_file_path}) as ydl:
            ydl.download([url])

        voice_client = ctx.voice_client

        voice_client.stop()
        voice_client.play(discord.FFmpegPCMAudio(temp_file_path, **self.ffmpeg_options))
        await ctx.send(f'Now playing from: {url}')

        # Clean up the temporary file
        os.remove(temp_file_path)

    @commands.command()
    async def leave(self, ctx):
        """Leaves the voice channel."""
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send('Disconnected from voice channel.')
        else:
            await ctx.send("I am not connected to any voice channel.")

    @commands.command()
    async def pause(self, ctx):
        """Pauses the current playback."""
        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("Playback paused.")
        else:
            await ctx.send("No audio is currently playing.")

    @commands.command()
    async def resume(self, ctx):
        """Resumes the paused playback."""
        if ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("Playback resumed.")
        else:
            await ctx.send("Audio is not paused.")

    @commands.command()
    async def stop(self, ctx):
        """Stops the current playback."""
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("Playback stopped.")
        else:
            await ctx.send("No audio is currently playing.")

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Sets the volume of the playback (0-100)."""
        if 0 <= volume <= 100:
            ctx.voice_client.source.volume = volume / 100
            await ctx.send(f"Volume set to {volume}%")
        else:
            await ctx.send("Volume must be between 0 and 100.")

# Setup function for adding the DJ cog to the bot
def setup(bot):
    bot.add_cog(DJ(bot))
