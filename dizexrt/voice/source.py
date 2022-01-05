import asyncio
import os
import random
from functools import partial

from typing import List

import youtube_dl
from gtts import gTTS

import discord

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
        return YTExtractInfo(data, ctx.author)

    @classmethod
    async def regather_stream(cls, data, *, loop):
        loop = loop or asyncio.get_event_loop()
        requester = data.author

        to_run = partial(ytdl.extract_info, url=data.url, download=False)
        data = await loop.run_in_executor(None, to_run)
        return cls(discord.FFmpegPCMAudio(data['url'], **ffmpeg_options), data=data, author=requester)

class LocalSource(discord.PCMVolumeTransformer):

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
        return LocalInfo(path, ctx.author)

    sources = [filename for filename in os.listdir(path) if filename != 'tts.mp3']
    @classmethod
    async def local(cls, ctx, index:int):
        if index <= len(cls.sources) and index > 0:
            path = f'{cls.path}/{cls.sources[index-1]}'
            await ctx.respond(f"**Now Start Talking** in {ctx.voice_client.channel.mention}")
            return LocalInfo(path, ctx.author)
        return None

    @classmethod
    async def random(cls, ctx):
        select = random.choice(cls.sources)
        path = f'{cls.path}/{select}'
        await ctx.respond(f"**Now Start Talking** in {ctx.voice_client.channel.mention}")
        return LocalInfo(path, ctx.author)

class LocalInfo:

    def __init__(self, path, author):
        self.id = path
        self.author = author
    
    def is_youtube(self) -> bool:
        return False

    def is_local(self) -> bool:
        return True

    def __eq__(self, source):
        try:
            source.is_local()
        except:
            return False
        
        if source.is_local():
            return True
        else:
            return False

class EmptySource:
    def __init__(self):
        pass

    def is_youtube(self) -> bool:
        return False

    def is_local(self) -> bool:
        return False

class YTInfo:

    def __init__(self, source, author):
        self.source = source
        self.author = author
        self.url = source.get('webpage_url')
    
    def is_youtube(self) -> bool:
        return True

    def is_local(self) -> bool:
        return False
    
    def __getattr__(self, item):
        return self.source.get(item)
    
    def __eq__(self, source):
        try:
            source.is_youtube()
        except:
            return False
        
        if source.is_youtube():
            return True
        else:
            return False

class YTExtractInfo:

    def __init__(self, source, author):
        self.source = source
        self.author = author
        self._source = self._extract()
    
    @property
    def count(self):
        return len(self._source)
    
    @property
    def playlist_title(self):
        return self._source[0]['playlist_title'] if 'entries' in self.source else None

    def is_playlist(self):
        return self._playlist

    def _extract(self):
        sources = []
        if 'entries' in self.source:
            self._playlist = True
            for data in self.source['entries']:
                sources.append(data)
        else:
            self._playlist = False
            sources.append(self.source)

        return sources
    
    @property
    def first(self) -> YTInfo:
        return YTInfo(self._source[0], self.author)

    @property
    def no_first(self) -> List[YTInfo]:
        return [YTInfo(_, self.author) for _ in self._source[1:]]
    
    @property
    def all(self) -> List[YTInfo]:
        return [YTInfo(_, self.author) for _ in self._source]