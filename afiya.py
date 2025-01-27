import discord
import discord.app_commands as app_commands
from discord.ext import commands
from discord.ui import Button, View
import asyncio
import yt_dlp
from dotenv import load_dotenv


#inbuild module
import os
import re

#local modules
import geturl  # Ensure this module has the function get_youtube_url
import getlyrics

def is_url(text):
    url_pattern = re.compile(
        r'^(https?://)?'         # http:// or https:// (optional)
        r'([a-zA-Z0-9.-]+)'      # Domain name
        r'(\.[a-zA-Z]{2,})'      # Top-level domain
        r'(/[^\s]*)?$'           # Optional path
    )
    return bool(url_pattern.match(text))

# Load the bot token
load_dotenv()
TOKEN = os.getenv('discord_token')

voice_clients = {}
yt_dl_options = {"format": "bestaudio/best"}
ytdl = yt_dlp.YoutubeDL(yt_dl_options)

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

class MusicControls(View):
    def __init__(self, voice_client,song_name):
        super().__init__(timeout=None)
        self.voice_client = voice_client
        self.song_name = song_name

    @discord.ui.button(label="Pause", style=discord.ButtonStyle.primary, emoji="⏸️")
    async def pause_button(self, interaction: discord.Interaction, button: Button):
        if self.voice_client.is_playing():
            self.voice_client.pause()
            await interaction.response.send_message("⏸️ Music paused.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ No music is currently playing.", ephemeral=True)

    @discord.ui.button(label="Resume", style=discord.ButtonStyle.success, emoji="▶️")
    async def resume_button(self, interaction: discord.Interaction, button: Button):
        if self.voice_client.is_paused():
            self.voice_client.resume()
            await interaction.response.send_message("▶️ Resumed the music.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ There's no paused music to resume.", ephemeral=True)

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger, emoji="⏺️")
    async def stop_button(self, interaction: discord.Interaction, button: Button):
        if self.voice_client.is_playing() or self.voice_client.is_paused():
            self.voice_client.stop()
            await self.voice_client.disconnect()
            await interaction.response.send_message("🛑 Music stopped and disconnected.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ I'm not playing anything.", ephemeral=True)
    
    @discord.ui.button(label="lyrics", style=discord.ButtonStyle.gray, emoji="📄")
    async def lyrics_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer()  # Prevents "interaction failed" errors
        try:
            await interaction.followup.send(f"🔍 Searching for lyrics of **{self.song_name}**...")
            song = getlyrics.get_song_lyrics(song_name=self.song_name)
            if song:
                # Genius API sometimes returns very long lyrics; split into chunks
                lyrics = song['lyrics']
                if len(lyrics) > 2000:
                    for i in range(0, len(lyrics), 2000):
                        await interaction.followup.send(lyrics[i:i+2000])
                else:
                    await interaction.followup.send(f"```{song['title']} by {song['artist']}\n\n{lyrics}```")
            else:
                await interaction.followup.send("❌ Lyrics not found.")
        except Exception as e:
            await interaction.followup.send(f"❌ Lyrics not found.")

    
    @discord.ui.button(label="About me", style=discord.ButtonStyle.gray, emoji="😉")
    async def about_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("**About me🙈** \n\n Hello! I’m **Afiya**, \n Your friendly music companion. I’m here to make your musical journey more enjoyable and meaningful. \n Whether you're looking for your favorite tunes, discovering new sounds, or simply relaxing with music,\n I’m always ready to find music. \n \n Developer : <@832496299249106944> \n Buy me a Coffee ☕ : https://buymeacoffee.com/hashmark \n Join our main server : https://discord.gg/Us2szPdKAa", ephemeral=True)
        

@bot.event
async def on_ready():
    print("Bot booted up")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Error syncing commands: {e}")

@bot.tree.command(name="hello", description="Say hello to the Afiya!")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hey {interaction.user.mention}! I'm Afiya, let's enjoy music together! 🎵", ephemeral=True)

@bot.tree.command(name="play", description="Play a song with buttons!")
@app_commands.describe(song_or_url="Enter a song name or YouTube URL")
async def play(interaction: discord.Interaction, song_or_url: str):
    if not interaction.user.voice or not interaction.user.voice.channel:
        await interaction.response.send_message("⚠️ You must be in a voice channel to use this command.", ephemeral=True)
        return

    voice_channel = interaction.user.voice.channel

    if interaction.guild.id not in voice_clients or not voice_clients[interaction.guild.id].is_connected():
        try:
            voice_client = await voice_channel.connect()
            voice_clients[interaction.guild.id] = voice_client
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to join the voice channel: {e}", ephemeral=True)
            return
    else:
        voice_client = voice_clients[interaction.guild.id]

    await interaction.response.send_message("🔍 Searching for your song...")

    try:
        if is_url(song_or_url):
            
            song_url = song_or_url
        else:
            song_url = geturl.get_youtube_url(song_or_url)
        
        if is_url(song_or_url):

            song_or_url = geturl.get_clean_song_name(song_or_url)

        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(song_url, download=False))

        song = data['url']
        player = discord.FFmpegPCMAudio(song, **ffmpeg_options)

        if not voice_client.is_playing():
            voice_client.play(player)
            controls = MusicControls(voice_client,song_or_url)
            await interaction.followup.send(f"**Now playing Enjoy Music!**😊 \n {song_url}", view=controls)
        else:
            await interaction.followup.send("⚠️ Already playing a song. Wait until it finishes or stop it first.")
    except Exception as e:
        await interaction.followup.send(f"❌ Error playing the song: {e}")

@bot.tree.command(name="stop", description="Stop the music and disconnect")
async def stop(interaction: discord.Interaction):
    voice_client = voice_clients.get(interaction.guild.id)

    if not voice_client or not voice_client.is_connected():
        await interaction.response.send_message("⚠️ I'm not connected to any voice channel.", ephemeral=True)
        return

    if voice_client.is_playing():
        voice_client.stop()
        await interaction.response.send_message("🛑 Music stopped.")
    else:
        await interaction.response.send_message("❌ I'm not playing anything.", ephemeral=True)

    await voice_client.disconnect()
    del voice_clients[interaction.guild.id]
    await interaction.followup.send("Byeee..See you Next time👋")

@bot.tree.command(name="pause", description="Pause the currently playing music")
async def pause(interaction: discord.Interaction):
    voice_client = voice_clients.get(interaction.guild.id)

    if not voice_client or not voice_client.is_connected():
        await interaction.response.send_message("⚠️ I'm not connected to any voice channel.", ephemeral=True)
        return

    if voice_client.is_playing():
        voice_client.pause()
        await interaction.response.send_message("⏸️ Music paused.")
    else:
        await interaction.response.send_message("❌ No music is currently playing.", ephemeral=True)

@bot.tree.command(name="resume", description="Resume the paused music")
async def resume(interaction: discord.Interaction):
    voice_client = voice_clients.get(interaction.guild.id)

    if not voice_client or not voice_client.is_connected():
        await interaction.response.send_message("⚠️ I'm not connected to any voice channel.", ephemeral=True)
        return

    if voice_client.is_paused():
        voice_client.resume()
        await interaction.response.send_message("▶️ Resumed the music.")
    else:
        await interaction.response.send_message("❌ There's no paused music to resume.", ephemeral=True)

@bot.tree.command(name="about", description="My details is here")
async def about(interaction: discord.Interaction):
    await interaction.response.send_message("**About me🙈** \n\n Hello! I’m **Afiya**, \n Your friendly music companion. I’m here to make your musical journey more enjoyable and meaningful. \n Whether you're looking for your favorite tunes, discovering new sounds, or simply relaxing with music,\n I’m always ready to find music. \n \n Developer : <@832496299249106944> \n Buy me a Coffee ☕ : https://buymeacoffee.com/hashmark \n Join our main server : https://discord.gg/Us2szPdKAa", ephemeral=True)

bot.run(TOKEN)
