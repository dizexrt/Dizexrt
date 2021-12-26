from discord.ext import commands

class MusicCommand(commands.Cog):

	def __init__(self, client):
		self.client = client
    
	@commands.command(aliases = ['say', 'speak', 'talk', 'tts'])
	async def gtts(self, ctx, *text:str):
		join = await ctx.bot.voice.join(ctx)
		if join:
			source = ctx.bot.voice.tts(*text)
			ctx.voice_client.play(source)

	@commands.command(aliases = ['p', 'play', 'search'])
	async def music_search(self, ctx, query:str):
		await ctx.alert(query)

	@commands.command()
	async def file(self, ctx):
		
		if len(ctx.message.attachments) > 0:
			for file in ctx.message.attachments:
				await ctx.send(file.filename.split('.')[1])

def setup(client):
    client.add_cog(MusicCommand(client))