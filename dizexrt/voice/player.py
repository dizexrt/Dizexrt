import asyncio
from async_timeout import timeout
import os
import random
import itertools
from functools import partial

import youtube_dl
from gtts import gTTS

import discord
from discord.ext import commands
from discord.commands import slash_command, Option

from dizexrt.view import MusicButton
import dizexrt

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ""

ytdl_format_options = {
    "format": "bestaudio/best",
    "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
    "restrictfilenames": True,
    "yesplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "auto",
    "source_address": "0.0.0.0",  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {"options": "-vn"}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, author, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.url = data.get('webpage_url')
        duration = data.get("duration")
        self.format_duration = f"{int(duration/3600):0>2}H:{int(duration%3600/60):0>2}M:{int(duration%3600%60):0>2}S"
    
    def __getattr__(self, item):
        return self.data.get(item)
    
    @classmethod
    async def create_source(cls, ctx, search: str, *, loop):
        loop = loop or asyncio.get_event_loop()

        to_run = partial(ytdl.extract_info, url=search, download=False)
        data = await loop.run_in_executor(None, to_run)

        data_info = []

        if 'entries' in data:
            for _data in data['entries']:
                data_info.append(YoutubeInfo(_data, ctx.author))
        else:
            data_info.append(YoutubeInfo(data, ctx.author))

        return data_info

    @classmethod
    async def regather_stream(cls, data, *, loop):
        loop = loop or asyncio.get_event_loop()
        requester = data.author

        to_run = partial(ytdl.extract_info, url=data.url, download=False)
        data = await loop.run_in_executor(None, to_run)

        return cls(discord.FFmpegPCMAudio(data['url'], **ffmpeg_options), data=data, author=requester)

class YoutubeInfo:

    def __init__(self, source, author):
        self.source = source
        self.author = author
        self.url = source['webpage_url']
    
    def __getattr__(self, item):
        return self.source.get(item)

class Source(discord.PCMVolumeTransformer):

    path = 'dizexrt/source/voices'

    def __init__(self, source, volume=0.5):
        super().__init__(source, volume)
    
    @classmethod
    def get(cls, source_id):
        return cls(discord.FFmpegPCMAudio(source_id, **ffmpeg_options))

    @classmethod
    async def tts(cls, ctx, *message):
        path = f'{cls.path}/tts.mp3'
        file = gTTS("".join(message), lang='th')
        file.save(path)
        await ctx.respond(f"**Now Start Talking** in {ctx.voice_client.channel.mention}")
        return LocalSourceInfo(path, ctx.author)

    sources = [filename for filename in os.listdir(path) if filename != 'tts.mp3']
    @classmethod
    async def local(cls, ctx, index:int):
        if index <= len(cls.sources) and index > 0:
            path = f'{cls.path}/{cls.sources[index-1]}'
            await ctx.respond(f"**Now Start Talking** in {ctx.voice_client.channel.mention}")
            return LocalSourceInfo(path, ctx.author)
        return None

    @classmethod
    async def random(cls, ctx):
        select = random.choice(cls.sources)
        path = f'{cls.path}/{select}'
        await ctx.respond(f"**Now Start Talking** in {ctx.voice_client.channel.mention}")
        return LocalSourceInfo(path, ctx.author)

class LocalSourceInfo:

    def __init__(self, path, author):
        self.id = path
        self.author = author

class MainPlayer:

    def __init__(self, ctx):
        self.ctx = ctx
        self.bot = ctx.bot
        self._guild = ctx.guild
        self._channel = ctx.channel
        self._cog = ctx.cog

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()
        self.volume = 0.5

        self.np = None
        self.current = asyncio.Queue(1)

        self.skip_loop = False
        self._loop = False
        self._loop_all = False

        ctx.bot.loop.create_task(self.player_loop())

    def loop(self):
        self._loop = not self._loop
        if self._loop:self._loop_all = False
        return self._loop
    
    def loop_all(self):
        self._loop_all = not self._loop_all
        if self._loop_all:self._loop = False
        return self._loop_all
    
    @property
    def queue_list(self):
        if self.queue.empty(): return None
        return list(itertools.islice(self.queue._queue,0,self.queue.qsize()))

    async def player_loop(self):
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()

            try:
                # Wait for the next song. If we timeout cancel the player and disconnect...
                async with timeout(180):  # 5 minutes...
                    if self._loop and not self.current.empty() and not self.skip_loop:
                        put_source = await self.current.get()
                    else:
                        put_source = await self.queue.get()

            except asyncio.TimeoutError:
                return await self.destroy(self._guild)
            
            if isinstance(put_source, YoutubeInfo):
                # Source was probably a stream (not downloaded)
                # So we should regather to prevent stream expiration
                try:
                    source = await YTDLSource.regather_stream(put_source, loop=self.bot.loop)
                except Exception as e:
                    await self._channel.send(f'There was an error processing your song.\n'
                                             f'```css\n[{e}]\n```')
                    continue
               
                try:
                    await self.update_queue()
                except:
                    pass
            elif isinstance(put_source, LocalSourceInfo):
                self._loop = False
                self.skip_loop = False
                self._loop_all = False
                try:
                    source = Source.get(put_source.id)
                except Exception as e:
                    await self._channel.send(f'There was an error processing your song.\n'
                                             f'```py\n[{e}]\n```')
                    await put_source.destroy()
                    continue
                    
            else:continue

            source.volume = self.volume

            if self._guild.voice_client is None:
                return await self.destroy(self._guild)

            self._guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))

            if isinstance(source, YTDLSource):
                view = MusicButton(self.bot, source.url, timeout = source.duration+10, loop = self._loop, loop_all = self._loop_all)
                self.np = await self._channel.send(embed = player_embed(source), view = view)

            await self.next.wait()

            source.cleanup()

            if isinstance(put_source, LocalSourceInfo):
                try:
                    await put_source.destroy()
                except:
                    pass
            
            if self._loop and not self.skip_loop:
                await self.current.put(put_source)
            else:
                self.current = asyncio.Queue(1)
                self.skip_loop = False

            try:
                await self.np.delete()
            except:
                pass
            
            if self._loop_all:
                await self.queue.put(put_source)

    async def destroy(self, guild):
        try:
            await self.np.delete()
        except:
            pass

        try:
            await self.update_queue()
        except:
            pass
        
        try:
            self.bot.loop.create_task(self._cog.cleanup(guild))
        except:
            pass

class PlayerManger:

    def __init__(self, client):
        self.client = client
    
    players = {}

    @staticmethod
    async def on_setup(client, message):

        async def ensure_voice(ctx):

            if ctx.author.voice is None:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author voice is none")
                return

            if ctx.voice_client is None:
                return await ctx.author.voice.channel.connect()
            
            if len(ctx.voice_client.channel.members) == 1:
                return await ctx.voice_client.move_to(ctx.author.voice.channel)
            
            if ctx.voice_client.channel != ctx.author.voice.channel:
                await ctx.send("Bot is already in voice channel with other.")
                raise commands.CommandError("Author is not in client channel")
                return
        
        try:
            music_channel = await message.guild.fetch_channel(dizexrt.db.get(message.guild, 'music:channel'))
        except:
            music_channel = None
        
        if message.channel == music_channel:
            if message.author.bot:return await message.edit(delete_after = 3)
            ctx = await client.get_context(message)
            await ensure_voice(ctx)
            await client.voice.play(ctx, message.content)
            return await message.delete()

    def loop(self, guild):
        player = self.players[guild.id]
        return player.loop()
    
    def loop_all(self, guild):
        player = self.players[guild.id]
        return player.loop_all()

    def get_queue(self, guild):
        try:
            queue = self.players[guild.id].queue_list
        except:
            queue = None
        return queue

    def get_player(self, ctx):
        try:
            player = self.players[ctx.guild.id]
        except:
            player = MainPlayer(ctx)
            self.players[ctx.guild.id] = player
        finally:
            return player
    
    async def play_source(self, ctx, index):
        player = self.get_player(ctx)
        source = await Source.local(ctx, index)
        if source is None:
            return await ctx.respond("There is no sound in this number", delete_after = 5)
        
        await player.queue.put(source)
    
    async def random_source(self, ctx):
        player = self.get_player(ctx)
        source = await Source.random(ctx)
        await player.queue.put(source)
    
    async def tts(self, ctx, *message):
        player = self.get_player(ctx)
        source = await Source.tts(ctx, *message)
        await player.queue.put(source)
    
    async def play(self, ctx, url):
        player = self.get_player(ctx)

        async with ctx.typing():
            sources = await YTDLSource.create_source(ctx, url, loop = ctx.bot.loop)
            for source in sources:
                await player.queue.put(source)

        return await ctx.send(embed = add_music_embed(sources))
    
    async def skip(self, guild):
        voice_client = guild.voice_client
        if voice_client.is_paused():
            pass
        elif not voice_client.is_playing():
            return
        player = self.players[guild.id]
        player.skip_loop = True
        voice_client.stop()
    
    async def stop(self, guild):
        try:
            await guild.voice_client.disconnect()
        except:
            pass

class PlayerCommand(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    async def cleanup(self, guild):
        del self.client.voice.players[guild.id]
        await guild.voice_client.disconnect()
    
    @slash_command(description = 'Let bot say something')
    async def random(self, ctx):
        await self.client.voice.random_source(ctx)

    say_option = Option(int, 'Enter number to say')
    @slash_command(description = 'Let bot say something')
    async def say(self, ctx, index:say_option):
        await self.client.voice.play_source(ctx, index)

    play_option = Option(str, 'Enter keywords or url of music')
    @slash_command(description = 'Play music from Youtube')
    async def play(self, ctx, query:play_option):
        await ctx.respond('Adding song to queue')
        await self.client.voice.play(ctx, query)
    
    tts_option = Option(str, 'Enter text to speak')
    @slash_command(description = 'Let bot say something')
    async def tts(self, ctx, message:tts_option):
        await self.client.voice.tts(ctx, *message)

    volume_option = Option(int, 'Enter volume 1-100')
    @slash_command(description = 'Change bot valume')
    async def volume(self, ctx, volume:volume_option):

        if ctx.voice_client is None:
            return await ctx.respond("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.respond(f"Changed volume to {volume}%")

    @slash_command(description = 'Let bot stop and disconnect')
    async def stop(self, ctx):
        await ctx.voice_client.disconnect()
        await ctx.respond(f'{ctx.author.mention} has disconnected bot from voice channel')

    @play.before_invoke
    async def ensure_voice(self, ctx):

        if ctx.author.voice is None:
            await ctx.respond("You are not connected to a voice channel.")
            raise commands.CommandError("Author voice is none")
            return

        if ctx.voice_client is None:
            return await ctx.author.voice.channel.connect()
        
        if len(ctx.voice_client.channel.members) == 1:
            return await ctx.voice_client.move_to(ctx.author.voice.channel)
        
        if ctx.voice_client.channel != ctx.author.voice.channel:
            await ctx.respond("Bot is already in voice channel with other.")
            raise commands.CommandError("Author is not in client channel")
            return
    
    @say.before_invoke
    @random.before_invoke
    @tts.before_invoke
    async def ensure_voice2(self, ctx):

        if ctx.author.voice is None:
            await ctx.respond("You are not connected to a voice channel.")
            raise commands.CommandError("Author voice is none")
            return

        if ctx.voice_client is None:
            await ctx.author.voice.channel.connect()
            return
        
        if len(ctx.voice_client.channel.members) == 1:
            await ctx.voice_client.disconnect()
            await ctx.author.voice.channel.connect()
            return
        
        if ctx.voice_client.channel == ctx.author.voice.channel:
            if ctx.voice_client.is_playing():
                await ctx.respond("Bot is busy now")
                raise commands.CommandError("Bot is not ready now!")

        if ctx.voice_client.channel != ctx.author.voice.channel:
            await ctx.respond("Bot is already in voice channel with other.")
            raise commands.CommandError("Author is not in client channel")

def add_music_embed(sources):
    amount = len(sources)
    if amount > 1:
        title = "Added Songs To Queue"
        description = f"`{amount}` songs from playlist : `{sources[0].playlist_title}`"
        embed = discord.Embed(title = title, description = description, colour = discord.Colour.green())
        return embed
    
    title = "Added Songs To Queue"
    description = f"Title : `{sources[0].title}`"
    embed = discord.Embed(title = title, description = description, colour = discord.Colour.green())
    return embed

def player_embed(source) -> discord.Embed:
    embed = discord.Embed(title = "Now Playing", colour = discord.Colour.purple())
    embed.add_field(name = source.channel, value = f"```\n{source.title}\n```", inline = False)
    embed.set_thumbnail(url = source.thumbnail)
    embed.set_footer(text = f'Duration : {source.format_duration}')
    return embed

def setup(client):
    client.add_cog(PlayerCommand(client))