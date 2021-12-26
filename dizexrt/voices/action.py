import discord
from gtts import gTTS

class Voice:

    def __init__(self, client) -> None:
        self.client = client

    async def join(self, ctx):

        if ctx.author.voice is None:
            await ctx.alert('You have to join voice channel first!')
            return False
        
        if ctx.voice_client is None:
            await ctx.author.voice.channel.connect()
            await ctx.alert(f'{self.client.user.name} has joined voice channel {ctx.voice_client.channel.mention} now')
            return True
        
        if ctx.voice_client.channel == ctx.author.voice.channel:
            return True
        
        if len(ctx.voice_client.channel.members) > 1:
            await ctx.alert(f'{self.client.user.name} has already joined voice channel with others')
            return False
        
        if len(ctx.voice_client.channel.members) == 1:
            await ctx.voice_client.move_to(ctx.author.voice.channel)
            ctx.alert(f'{self.client.user.name} is moved to voice channel {ctx.voice_client.channel.mention}')
            return True
    
    def tts(self, *message:str):
        tts_path = 'dizexrt/voices/source/tts.mp3'
        #FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        tts = gTTS(" ".join(message), lang = 'th')
        tts.save(tts_path)
        return discord.FFmpegPCMAudio(tts_path)
