import asyncio
import time
import discord
from discord import FFmpegPCMAudio
from discord.ext import commands
from youtube_dl import YoutubeDL
import requests
import lyricsgenius as lg
genius = lg.Genius('key', skip_non_songs=True, excluded_terms=["(Remix)", "(Live)"], remove_section_headers=True)
def getlyrics(video):
    song = genius.search_song(title=video["playlist"],artist=video["artist"])
    lyrics = song.lyrics
    return lyrics[:-29]
async def gettime(self):
    while self.voice_client.is_playing() == True:
        self.time += 1
        await asyncio.sleep(1)
async def nextque(self):
    while self.query != []:
        if self.voice_client != None:
            if self.lop == False:
                if self.voice_client.is_playing() == False:
                    if self.voice_client.is_paused() == False:
                        self.query.pop(0)
                        if self.query != []:
                            self.time = 0
                            video = self.query[0]
                            self.np = video['title']
                            source = video['formats'][0]['url']
                            self.voice_client.play(FFmpegPCMAudio(source, executable="C:\\ffmpeg\\bin\\ffmpeg.exe"))
                            emb = discord.Embed(title="Now playing", description=f"[{video['title']}]({video['webpage_url']})\n**Uploader:** {video['uploader']}", color=0xff2700)
                            emb.set_thumbnail(url=video['thumbnail'])
                            await self.voice_context.send(embed=emb)
                            await gettime(self)
            if self.lop == True:
                if self.voice_client.is_playing() == False:
                    if self.voice_client.is_paused() == False:
                        self.time = 0
                        video = self.query[0]
                        source = video['formats'][0]['url']
                        self.voice_client.play(FFmpegPCMAudio(source, executable="C:\\ffmpeg\\bin\\ffmpeg.exe"))
                        emb = discord.Embed(title="Now playing", description=f"[{video['title']}]({video['webpage_url']})\n**Uploader:** {video['uploader']}", color=0xff2700)
                        emb.set_thumbnail(url=video['thumbnail'])
                        await self.voice_context.send(embed=emb)
                        await gettime(self)
        await asyncio.sleep(.01)
def search(query):
    with YoutubeDL({'format': 'bestaudio', 'noplaylist': 'True'}) as ydl:
        try:
            requests.get(query)
        except:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
        else:
            info = ydl.extract_info(query, download=False)
    return info
class Music(commands.Cog):
    
    def __init__(self, client):
        self.client = client
        self.query = []
        self.voice_client = None
        self.voice_context = None
        self.np = None
        self.lop = False
        self.time = 0
    @commands.command(name="Loop",help="Loops the current song that is playing",aliases=["loop"])
    async def loop(self, context):
        if self.query != []:
            fin = False
            if self.lop == False:
                if fin == False:
                    fin = True
                    self.lop = True
            if self.lop == True:
                if fin == False:
                    fin = True
                    self.lop = False
            await context.reply(f"Set loop to: {self.lop}")
    @commands.command(name="NowPlaying",help="shows what is currently playing",aliases=["nowplaying","NP","np"])
    async def nowplaying(self, context):
        x = time.strftime('%H:%M:%S', time.gmtime(self.time))
        y = time.strftime('%H:%M:%S', time.gmtime(int(self.query[0]["duration"])))
        emb = discord.Embed(title="Now playing", description=f"**{self.np}**\n{x}/{y}",color=0xff2700)
        await context.send(embed=emb)
    @commands.command(name="ClearQueue",help="clears the queue", aliases=["clearqueue","cq","CQ"])
    async def clearqueue(self, context):
        now = True
        for item in self.query:
            if now == True:
                now = False
            else:
                self.query.remove(item)
        await context.send("Cleared the queue!")
    @commands.command(name="Skip,",help="skips the current song",aliases=["skip","S","s"])
    async def skip(self, context):
        self.voice_client.stop()
        await context.send("Skipped")
    @commands.command(name="Queue",help="lists songs in queue",aliases=["queue","Q","q"])
    async def queue(self, context):
        now = True
        num = 0 
        queue = self.query
        desc = ""
        for item in queue:
            if now != True:
                num +=1
                desc += f"**{num}. {item['title']}**\n"
            else:
                now = False
                desc += f"**Now playing: {item['title']}**\n\n"
        if desc == "":
            desc = "Queue is empty"
        emb = discord.Embed(title="Queue", description=desc)
        await context.send(embed=emb)
    @commands.command(name="Remove",help="Removes an item in the queue.", aliases=["remove"])
    async def remove(self, context, message: int):
        queue = self.query
        now = True
        items = 0

        for item in queue:
            if now != True:
                items += 1
            else:
                now = False
        if message <= items:
            if message <= 0:
                await context.send("That is not an item in the queue!")
            else:
                video = queue[0]
                queue.pop(message)
                await context.send(f"Successfully removed **{video['title']}** from the queue!")
        else:
            await context.send("That is not an item in the queue!")
        
    @commands.command(name="Join",help="joins the channel the author is in", aliases=["join", "J", "j"])
    async def join(self, context):
        member_voice = context.author.voice
        if member_voice and member_voice.channel:
            if context.voice_client:
                await context.send("Bot already in a voice channel!")
            else:
                try:
                    await member_voice.channel.connect()
                    self.voice_client = context.voice_client
                    await context.send("Successfully connected to voice channel!")
                except:
                    await context.send("An error occured make sure you're in a voice channel!")
        else:
            await context.send("You must be in a channel!")
    @commands.command(name="Pause",help="Pauses the current song that's playing", aliases=["pause"])
    async def pause(self, context):
        if self.voice_client.is_playing() == False:
            if self.voice_client.is_paused() == False:
                await context.send("No music to pause!")
        if self.voice_client.is_paused() == True:
            await context.send("Music already paused")
        else:
            self.voice_client.pause()
            await context.message.add_reaction("✅")
    @commands.command(name="Resume",help="Resumes the song that was playing", aliases=["resume", "R", "r"])
    async def resume(self, context):
        if self.voice_client.is_paused() == True:
            self.voice_client.resume()
            await context.message.add_reaction("✅")
        else:
            await context.send("Bot not paused")
    @commands.command(name="Stop",help="Stops the current song that's playing", aliases=["stop"])
    async def stop(self, context):
        self.query.clear()
        self.voice_client.stop()
        self.lop = False
        await context.message.add_reaction("✅")
    @commands.command(name="Leave",help="Leaves the channel the bot is currently in", aliases=["leave", "L", "l","dis","Dis","disconnect","Disconnect"])
    async def Leave(self, context):
        member_voice = context.author.voice
        if member_voice and member_voice.channel:
            if context.voice_client:
                if member_voice.channel == context.voice_client.channel:
                    try:
                        if context.voice_client.is_playing():
                            context.voice_client.stop()
                            await context.voice_client.disconnect()
                            await context.send("Successfully disconnected to voice channel!")
                            self.voice_client = None
                            self.voice_context = None
                            self.query = None
                            self.np = None
                            self.lop = False
                        else:
                            await context.voice_client.disconnect()
                            await context.send("Successfully disconnected to voice channel!")
                    except:
                        await context.send("An error occured!")
                else:
                    await context.send("You must be in the same voice channel as the bot!")
            else:
                await context.send("Bot is not in a voice channel!")
    @commands.command(name="Play",help="Plays a song", aliases=["play","P","p"])
    async def play(self, context,*,query):
        member_voice = context.author.voice
        if member_voice and member_voice.channel:
            if context.voice_client:
                pass
            else:
                await member_voice.channel.connect()
            if self.query != []:
                video = search(query)
                emb = discord.Embed(title=f"✅ Queued {video['title']}", color=0xff2700)
                self.query.append(video)
                await context.send(embed=emb)
            if self.query == []:
                client_voice = context.voice_client
                self.voice_client = context.voice_client
                self.voice_context = context
                await context.trigger_typing()
                video = search(query)
                source = video['formats'][0]['url']
                emb = discord.Embed(title="Now playing", description=f"[{video['title']}]({video['webpage_url']})\n**Uploader:** {video['uploader']}", color=0xff2700)
                emb.set_thumbnail(url=video['thumbnail'])
                client_voice.play(FFmpegPCMAudio(source,executable="C:\\ffmpeg\\bin\\ffmpeg.exe"))
                self.np = video["title"]
                self.query.append(video)
                await context.send(embed=emb)
                await gettime(self)
                await nextque(self)
def setup(client):
    client.add_cog(Music(client))
