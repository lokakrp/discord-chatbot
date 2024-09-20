import discord
from discord.ext import commands
import yt_dlp

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}
YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': True}

class MusicBot(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.queue = []
        self.currently_playing = None  # Now playing

    @discord.app_commands.command(name="play", description="Play a song from YouTube")  # Play
    async def play(self, interaction: discord.Interaction, search: str):
        voice_channel = interaction.user.voice.channel if interaction.user.voice else None
        if not voice_channel:
            return await interaction.response.send_message("You're not in a voice channel!")
        if not interaction.guild.voice_client:
            await voice_channel.connect()

        await interaction.response.defer()
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(f"ytsearch:{search}", download=False)
            if 'entries' in info:
                info = info['entries'][0]
            url = info['url']
            title = info['title']
            self.queue.append((url, title))
            await interaction.followup.send(f'Added to queue: **{title}**')

        if not interaction.guild.voice_client.is_playing():
            await self.play_next(interaction)

    async def play_next(self, interaction: discord.Interaction):
        if self.queue:
            url, title = self.queue.pop(0)
            self.currently_playing = title  # Set currently playing song
            source = discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS)  # Use FFmpegPCMAudio
            interaction.guild.voice_client.play(source, after=lambda _: self.client.loop.create_task(self.play_next(interaction)))
            await interaction.followup.send(f'Now playing: **{title}**')
        elif not interaction.guild.voice_client.is_playing():
            await interaction.followup.send("Queue is empty!")

    @discord.app_commands.command(name="skip", description="Skip the current song")  # Skip
    async def skip(self, interaction: discord.Interaction):
        if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
            interaction.guild.voice_client.stop()
            await interaction.response.send_message("Skipped ⏭")
        else:
            await interaction.response.send_message("No song is currently playing!")

    @discord.app_commands.command(name="leave", description="Disconnect from the voice channel")  # Leave
    async def leave(self, interaction: discord.Interaction):
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect()
            await interaction.response.send_message("Disconnected from the voice channel.")
        else:
            await interaction.response.send_message("I'm not in a voice channel!")

    @discord.app_commands.command(name="np", description="Show the currently playing song")  # Now playing
    async def now_playing(self, interaction: discord.Interaction):
        """Show the currently playing song"""
        if self.currently_playing:
            await interaction.response.send_message(f'Currently playing: **{self.currently_playing}**')
        else:
            await interaction.response.send_message("No song is currently playing.")

    @discord.app_commands.command(name="queue", description="Show the current song queue")  # Queue
    async def queue(self, interaction: discord.Interaction):
        """Show the current song queue"""
        if self.queue:
            queue_list = '\n'.join([f"{i+1}. {title}" for i, (_, title) in enumerate(self.queue)])
            await interaction.response.send_message(f'Current queue:\n{queue_list}')
        else:
            await interaction.response.send_message("The queue is empty.")

    @discord.app_commands.command(name="remove", description="Remove a song from the queue by its position")  # Remove by index
    async def remove(self, interaction: discord.Interaction, index: int):
        """Remove a song from the queue by its index"""
        if 0 < index <= len(self.queue):
            removed_song = self.queue.pop(index - 1)[1]
            await interaction.response.send_message(f'Removed **{removed_song}** from the queue.')
        else:
            await interaction.response.send_message(f'Invalid index! Please provide a number between 1 and {len(self.queue)}.')

    @discord.app_commands.command(name="clear", description="Clear the entire queue except for the currently playing song")  # Clear queue
    async def clear(self, interaction: discord.Interaction):
        """Clear the entire queue except for the currently playing song"""
        self.queue.clear()  # Clear the queue
        await interaction.response.send_message("The queue has been cleared except for the currently playing song.")

async def setup(client):
    await client.add_cog(MusicBot(client))
