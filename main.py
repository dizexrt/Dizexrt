import os
from dizexrt import MyClient
from online import keep_alive
from discord_slash import SlashCommand

token = os.environ['token']

client = MyClient()
slash = SlashCommand(client, sync_commands=True)

@client.message_command()
async def hello(ctx, message):
	await message.add_reaction('😊')

@client.slash_command()
async def moix(ctx):
	await ctx.send("Hello")

client.load_extension_folder('cogs')
keep_alive()
client.run(token)