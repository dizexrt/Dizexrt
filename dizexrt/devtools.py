import discord

class FileManager:

	file_types = ['py', 'cs']

	def __init__(self, client):
		self.client = client
	
	def get(self, guild, find):
		for emoji in guild.emojis:
			if emoji.name == find:
				return emoji

	async def get_emoji(self, guild):
		custom = self.file_types.copy()

		for emoji in guild.emojis:
			if emoji.name in self.file_types:
				custom.remove(emoji.name)
		
		if len(custom) == 0: return

		for emoji in custom:
			await guild.create_custom_emoji(name = emoji, image = f'dizexrt/emojis/{emoji}.png')

	async def recognizes(self, message:discord.Message):
		await self.get_emoji(message.guild)

		if len(message.attachments) > 0:

			types = []

			for file in message.attachments:
				suffix = file.filename.split('.')[1]
				types.append(suffix)
			
			for suffix in types:
				if suffix in self.file_types:
					await message.add_reaction(self.get(message.guild, suffix))
			
