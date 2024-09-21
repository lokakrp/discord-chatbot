import discord
from discord.ext import commands
import yt_dlp

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}
YDL_OPTIONS = {
    'format': 'bestaudio',
    'noplaylist': True,
    'extract_flat': True  # Use this for faster extraction, can help with SoundCloud
}

class MusicBot(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.queue = []
        self.currently_playing = None  # Now playing

    @discord.app_commands.command(name="play", description="play a song from youtube or soundcloud")
    async def play(self, interaction: discord.Interaction, search: str):
        voice_channel = interaction.user.voice.channel if interaction.user.voice else None
        
        if not voice_channel:
            return await interaction.response.send_message("uou're not in a voice channel!!")

        if not interaction.guild.voice_client:
            await voice_channel.connect()

        await interaction.response.defer()

        try:
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(search, download=False)
                if 'entries' in info:
                    info = info['entries'][0]  # Get the first entry if it's a playlist

                url = info['url']
                title = info['title']

            self.queue.append((url, title))
            await interaction.followup.send(f'added to queue: **{title}**')

            if not interaction.guild.voice_client.is_playing():
                await self.play_next(interaction)
        except yt_dlp.utils.YoutubeDLError as e:
            await interaction.followup.send(f"YT-DLP Error: {str(e)}")
        except Exception as e:
            await interaction.followup.send(f"an error occurred: {str(e)}")

    async def play_next(self, interaction: discord.Interaction):
        if self.queue:
            url, title = self.queue.pop(0)
            self.currently_playing = title  # Set currently playing song
            source = discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS)

            interaction.guild.voice_client.play(source, after=lambda _: self.client.loop.create_task(self.play_next(interaction)))
            await interaction.followup.send(f'Now playing: **{title}**')
        else:
            self.currently_playing = None
            await interaction.followup.send("queue is empty!")

    @discord.app_commands.command(name="skip", description="skip the current song")
    async def skip(self, interaction: discord.Interaction):
        if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
            interaction.guild.voice_client.stop()
            await interaction.response.send_message("skipped current song!!")
        else:
            await interaction.response.send_message("no song is currently playing!")

    @discord.app_commands.command(name="leave", description="disconnect from the voice channel")
    async def leave(self, interaction: discord.Interaction):
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect()
            await interaction.response.send_message("disconnected from the voice channel.")
        else:
            await interaction.response.send_message("i'm not in a voice channel!")

    @discord.app_commands.command(name="np", description="show the currently playing song")
    async def now_playing(self, interaction: discord.Interaction):
        if self.currently_playing:
            await interaction.response.send_message(f'currently playing: **{self.currently_playing}**')
        else:
            await interaction.response.send_message("no song is currently playing.")

    @discord.app_commands.command(name="queue", description="show the current song queue")
    async def queue(self, interaction: discord.Interaction):
        if self.queue:
            queue_list = '\n'.join([f"{i + 1}. {title}" for i, (_, title) in enumerate(self.queue)])
            await interaction.response.send_message(f'current queue:\n{queue_list}')
        else:
            await interaction.response.send_message("the queue is empty.")

    @discord.app_commands.command(name="remove", description="remove a song from the queue by its position")
    async def remove(self, interaction: discord.Interaction, index: int):
        if 0 < index <= len(self.queue):
            removed_song = self.queue.pop(index - 1)[1]
            await interaction.response.send_message(f'removed **{removed_song}** from the queue.')
        else:
            await interaction.response.send_message(f'invalid index! please provide a number between 1 and {len(self.queue)}.')

    @discord.app_commands.command(name="clear", description="clear the entire queue except for the currently playing song")
    async def clear(self, interaction: discord.Interaction):
        self.queue.clear()
        await interaction.response.send_message("the queue has been cleared except for the currently playing song.")

async def setup(client):
    await client.add_cog(MusicBot(client))
