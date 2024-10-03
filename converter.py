import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
from moviepy.editor import VideoFileClip
import os

class MediaConverter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cache_dir = os.path.join(os.path.dirname(__file__), '__pycache__')
        os.makedirs(self.cache_dir, exist_ok=True)

    async def send_file(self, interaction, file_path):
        if os.path.exists(file_path):
            await interaction.response.send_message(file=discord.File(file_path))
            os.remove(file_path)  # Clean up after sending
        else:
            await interaction.response.send_message("file not found.")

    # download functions
    async def download_youtube(self, interaction, url, format):
        ydl_opts = {
            'format': 'bestaudio/best' if format == 'mp3' else 'bestvideo+bestaudio',
            'outtmpl': os.path.join(self.cache_dir, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio' if format == 'mp3' else 'FFmpegVideoConvertor',
                'preferredcodec': format,
                'preferredquality': '192',
            }],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            await interaction.response.send_message(f'downloading from YouTube: {url}...')
            ydl.download([url])
            info = ydl.extract_info(url, download=False)
            file_path = os.path.join(self.cache_dir, f"{info['title']}.{format}")
            await self.send_file(interaction, file_path)

    async def download_soundcloud(self, interaction, url):
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(self.cache_dir, '%(title)s.%(ext)s'),
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            await interaction.response.send_message(f'downloading from SoundCloud: {url}...')
            ydl.download([url])
            info = ydl.extract_info(url, download=False)
            file_path = os.path.join(self.cache_dir, f"{info['title']}.mp3")
            await self.send_file(interaction, file_path)

    async def download_spotify(self, interaction, url):
        await interaction.response.send_message("Ddwnloading from Spotify is not yet implemented.")

    async def download_twitter(self, interaction, url):
        ydl_opts = {
            'format': 'bestvideo+bestaudio',
            'outtmpl': os.path.join(self.cache_dir, '%(title)s.%(ext)s'),
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            await interaction.response.send_message(f'downloading from twitter: {url}...')
            ydl.download([url])
            info = ydl.extract_info(url, download=False)
            file_path = os.path.join(self.cache_dir, f"{info['title']}.mp4")
            await self.send_file(interaction, file_path)

    async def download_tiktok(self, interaction, url):
        ydl_opts = {
            'format': 'bestvideo+bestaudio',
            'outtmpl': os.path.join(self.cache_dir, '%(title)s.%(ext)s'),
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            await interaction.response.send_message(f'downloading from tiktok: {url}...')
            ydl.download([url])
            info = ydl.extract_info(url, download=False)
            file_path = os.path.join(self.cache_dir, f"{info['title']}.mp4")
            await self.send_file(interaction, file_path)

    async def download_instagram(self, interaction, url, format):
        ydl_opts = {
            'format': 'bestvideo+bestaudio',
            'outtmpl': os.path.join(self.cache_dir, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio' if format == 'mp3' else 'FFmpegVideoConvertor',
                'preferredcodec': format,
                'preferredquality': '192',
            }],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            await interaction.response.send_message(f'downloading from Instagram: {url}...')
            ydl.download([url])
            info = ydl.extract_info(url, download=False)
            file_path = os.path.join(self.cache_dir, f"{info['title']}.{format}")
            await self.send_file(interaction, file_path)

    # File conversion functions
    async def convert_mp4_to_mp3(self, interaction, file_path):
        if os.path.exists(file_path):
            mp3_path = os.path.join(self.cache_dir, f"{os.path.splitext(os.path.basename(file_path))[0]}.mp3")
            clip = VideoFileClip(file_path)
            clip.audio.write_audiofile(mp3_path)
            await self.send_file(interaction, mp3_path)
        else:
            await interaction.response.send_message("file not found.")

    async def convert_mp4_to_gif(self, interaction, file_path):
        if os.path.exists(file_path):
            gif_path = os.path.join(self.cache_dir, f"{os.path.splitext(os.path.basename(file_path))[0]}.gif")
            clip = VideoFileClip(file_path)
            clip.write_gif(gif_path)
            await self.send_file(interaction, gif_path)
        else:
            await interaction.response.send_message("file not found.")

    async def convert_gif_to_mp4(self, interaction, file_path):
        if os.path.exists(file_path):
            gif_clip = VideoFileClip(file_path)
            mp4_path = os.path.join(self.cache_dir, f"{os.path.splitext(os.path.basename(file_path))[0]}.mp4")
            gif_clip.write_videofile(mp4_path)
            await self.send_file(interaction, mp4_path)
        else:
            await interaction.response.send_message("file not found.")

    async def convert_webm_to_mp4(self, interaction, file_path):
        if os.path.exists(file_path):
            clip = VideoFileClip(file_path)
            mp4_path = os.path.join(self.cache_dir, f"{os.path.splitext(os.path.basename(file_path))[0]}.mp4")
            clip.write_videofile(mp4_path)
            await self.send_file(interaction, mp4_path)
        else:
            await interaction.response.send_message("file not found.")

    # commands
    @app_commands.command(name='yt to mp4', description="download a youtube video as MP4.")
    async def youtube_to_mp4(self, interaction: discord.Interaction, url: str):
        await self.download_youtube(interaction, url, 'mp4')

    @app_commands.command(name='yt to mp3', description="download a youTube video as MP3.")
    async def youtube_to_mp3(self, interaction: discord.Interaction, url: str):
        await self.download_youtube(interaction, url, 'mp3')

    @app_commands.command(name='soundcloud to mp3', description="download a soundCloud track as MP3.")
    async def soundcloud_to_mp3(self, interaction: discord.Interaction, url: str):
        await self.download_soundcloud(interaction, url)

    @app_commands.command(name='spotify to mp3', description="download a spotify track as MP3.")
    async def spotify_to_mp3(self, interaction: discord.Interaction, url: str):
        await self.download_spotify(interaction, url)

    @app_commands.command(name='twitter to mp4', description="download a twitter video as MP4.")
    async def twitter_to_mp4(self, interaction: discord.Interaction, url: str):
        await self.download_twitter(interaction, url)

    @app_commands.command(name='tiktok to mp4', description="download a tiktok video as MP4.")
    async def tiktok_to_mp4(self, interaction: discord.Interaction, url: str):
        await self.download_tiktok(interaction, url)

    @app_commands.command(name='instagram to mp4', description="download an instagram video as MP4.")
    async def instagram_to_mp4(self, interaction: discord.Interaction, url: str):
        await self.download_instagram(interaction, url, 'mp4')

    @app_commands.command(name='instagram to mp3', description="download an instagram video as MP3.")
    async def instagram_to_mp3(self, interaction: discord.Interaction, url: str):
        await self.download_instagram(interaction, url, 'mp3')

    @app_commands.command(name='mp4 to mp3', description="convert MP4 video to MP3 audio.")
    async def mp4_to_mp3(self, interaction: discord.Interaction, file_path: str):
        await self.convert_mp4_to_mp3(interaction, file_path)

    @app_commands.command(name='mp4 to gif', description="convert MP4 video to GIF.")
    async def mp4_to_gif(self, interaction: discord.Interaction, file_path: str):
        await self.convert_mp4_to_gif(interaction, file_path)

    @app_commands.command(name='gif to mp4', description="convert GIF to MP4 video.")
    async def gif_to_mp4(self, interaction: discord.Interaction, file_path: str):
        await self.convert_gif_to_mp4(interaction, file_path)

    @app_commands.command(name='webm to mp4', description="convert WebM video to MP4.")
    async def webm_to_mp4(self, interaction: discord.Interaction, file_path: str):
        await self.convert_webm_to_mp4(interaction, file_path)

# setup function
async def setup(bot):
    await bot.add_cog(MediaConverter(bot))
