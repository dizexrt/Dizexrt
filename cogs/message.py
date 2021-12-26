from discord.ext import commands

class Message(commands.Cog):

	def __init__(self, client):
		self.client = client

	@commands.Cog.listener()
	async def on_message(self, message):

		if len(message.attachments) > 0:
			await self.client.file_manager.recognizes(message)


def setup(client):

	client.add_cog(Message(client))