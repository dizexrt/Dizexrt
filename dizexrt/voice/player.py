import asyncio
from async_timeout import timeout

import discord
from discord.ext import commands
from discord.commands import slash_command, Option

from ..view import MusicView
from .source import YTDLSource, LocalSource, YTExtractInfo
from .queue import MusicQueue

class MainPlayer:

    def __init__(self, ctx):
        self.ctx = ctx
        self.bot = ctx.bot
        self._guild = ctx.guild
        self._channel = ctx.channel
        self._cog = ctx.cog

        self.queue = MusicQueue()
        self.next = asyncio.Event()
        self.volume = 0.5

        self.np = None

        ctx.bot.loop.create_task(self.player_loop())

    def loop(self):
        return self.queue.loop_current()
    
    def loop_all(self):
        return self.queue.loop_all()
    
    def skip_loop(self):
        return self.queue.skip_loop()

    async def player_loop(self):
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()
            try:
                async with timeout(180):
                    _source = await self.queue.get()
            except asyncio.TimeoutError:
                return await self.destroy(self._guild)
            
            if _source.is_youtube():
                try:
                    source = await YTDLSource.regather_stream(_source, loop=self.bot.loop)
                except Exception as e:
                    await self._channel.send(f'There was an error processing your song.\n'
                                             f'```css\n[{e}]\n```')
                    continue

            elif _source.is_local():
                try:
                    source = LocalSource.get(_source.id)
                except Exception as e:
                    await self._channel.send(f'There was an error processing your song.\n'
                                             f'```py\n[{e}]\n```')
                    continue
                    
            else:continue

            source.volume = self.volume

            if self._guild.voice_client is None:
                return await self.destroy(self._guild)

            self._guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))

            if isinstance(source, YTDLSource):
                view = MusicView(self.bot, source.url, timeout = source.duration+10, loop = self.queue.get_loop(), loop_all = self.queue.get_loop_all())
                self.np = await self._channel.send(embed = player_embed(source), view = view)

            await self.next.wait()

            source.cleanup()
            
            try:
                await self.np.delete()
            except:
                pass

    async def destroy(self, guild):
        try:
            await self.np.delete()
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

    def loop(self, guild):
        player = self.players[guild.id]
        return player.loop()
    
    def loop_all(self, guild):
        player = self.players[guild.id]
        return player.loop_all()

    def get_queue(self, guild):
        try:
            player = self.players[guild.id]
        except:
            return None

        return player.queue.items

    def get_player(self, ctx):
        try:
            player = self.players[ctx.guild.id]
        except:
            player = MainPlayer(ctx)
            self.players[ctx.guild.id] = player
        return player
    
    async def play_source(self, ctx, index):
        player = self.get_player(ctx)
        source = await LocalSource.local(ctx, index)
        if source is None:
            return await ctx.respond("There is no sound in this number", delete_after = 5)
        await player.queue.put(source)
    
    async def random_source(self, ctx):
        player = self.get_player(ctx)
        source = await LocalSource.random(ctx)
        await player.queue.put(source)
    
    async def tts(self, ctx, *message):
        player = self.get_player(ctx)
        source = await LocalSource.tts(ctx, *message)
        await player.queue.put(source)
    
    async def play(self, ctx, url):
        player = self.get_player(ctx)
        source = await YTDLSource.create_source(ctx, url, loop = ctx.bot.loop)
        await player.queue.put(source.first)
        if source.is_playlist():
            await player.queue.put(*source.no_first)
        return await ctx.send(embed = add_music_embed(source))
    
    async def skip(self, guild):
        voice_client = guild.voice_client
        if voice_client.is_paused():
            pass
        elif not voice_client.is_playing():
            return
        player = self.players[guild.id]
        player.skip_loop()
        voice_client.stop()
    
    async def stop(self, guild):
        try:
            await guild.voice_client.disconnect()
        except:
            pass

    async def clear_queue(self, guild):
        player = self.players[guild.id]
        await player.queue.cleanup()

    async def edit_queue(self, channel):
        player = self.players[channel.guild.id]
        await channel.send('Input number of music that you want to delete\n```example : 1 2 3 5 17\n```')
        try:
            message = await self.client.wait_for('message', timeout = 30)
        except:
            return
        await player.queue.delete(*[int(i) for i in message.content.split(' ') if i.isnumeric()])
    
    def fqueue(self, guild) -> discord.Embed:
        player = self.players[guild.id]
        queue = player.queue.items
        fmt = "```\n"
        for i in range(len(queue)):
            fmt += f'{i+1} {queue[i].title}\n'
        fmt += '\n```'
        embed = discord.Embed(title=f'Upcoming - Next {len(queue)}', description=fmt, colour = discord.Colour.blue())
        embed.set_author(name = 'Queue')
        return embed

class PlayerCommand(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    async def cleanup(self, guild):
        del self.client.voice.players[guild.id]
        try:
            await guild.voice_client.disconnect()
        except:pass
    
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
        async with ctx.typing():
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

def add_music_embed(source:YTExtractInfo) -> discord.Embed:
    if source.is_playlist():
        title = "Added Songs To Queue"
        description = f"`{source.count}` songs from playlist : `{source.playlist_title}`"
        embed = discord.Embed(title = title, description = description, colour = discord.Colour.green())
        return embed
    
    title = "Added Songs To Queue"
    description = f"Title : `{source.first.title}`"
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