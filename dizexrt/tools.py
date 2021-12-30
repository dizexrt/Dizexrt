import discord
from dizexrt.view import UrlButton

class MessageTools:

	def __init__(self, client):
		self.client = client
		self.url = UrlManager(client)
		self.file = FileManager(client)

	async def identify(self, message):
		message = Recognize(message)

		if message.is_url() and message.is_embed():
			await self.url.extract_domain(message)
			await message.delete()
			return

		if message.is_file():
			await self.file.identify(message)
			return
	
	async def extract_file(self, message):
		message = Recognize(message)
		if message.is_file():
			await self.file.identify(message)
	
	async def extract_url(self, message):
		message = Recognize(message)
		if message.is_url() and message.is_embed():
			await self.url.extract_domain(message)
			await message.delete()

class Recognize:

	def __init__(self, message):
		self.message = message
	
	def __getattr__(self, item):
		return self.message.__getattribute__(item)

	def is_url(self):
		if self.message.content.startswith('https://') or self.message.content.startswith('http://'):
			return True
		return False

	def is_file(self):
		if len(self.message.attachments) > 0:
			return True
		return False

	def is_embed(self):
		if len(self.message.embeds) > 0:
			return True
		return False

class _Base:

	def __init__(self, client, emojis):
		self.client = client
		self.emojis = emojis
		
	async def get_emoji(self, guild, find):
		if find is None:return None

		for emoji in guild.emojis:
			if emoji.name == find:
				return emoji
		
		if find not in self.emojis:return None
		
		path = f'dizexrt/emojis/{find}.png'
		with open(path, "rb") as imageFile:
			image = imageFile.read()
		
		return await guild.create_custom_emoji(name = find, image = image)

class UrlManager(_Base):

	def __init__(self, client):
		self.domains = ['github']
		super().__init__(client, self.domains)
	
	def get_domain(self, url):
		for domain in self.domains:
			if domain in url:
				return domain
		return None
	
	async def extract_domain(self, message):
		embed = message.embeds[0]
		embed.colour = discord.Colour.purple()
		message = await message.channel.send(embed = embed, view = UrlButton(embed.url))

		domain = self.get_domain(embed.url)
		emoji = await self.get_emoji(message.guild, domain)

		if emoji is None:return

		await message.add_reaction(emoji)

class FileManager(_Base):

	def __init__(self, client):
		emojis = ['py', 'cs', 'txt', 'docx']
		super().__init__(client, emojis)
	
	async def identify(self, message:discord.Message):

		if len(message.attachments) > 0:

			file_suffixes = [attachment.filename.split('.')[1] for attachment in message.attachments]
	
			for suffix in file_suffixes:
				emoji = await self.get_emoji(message.guild, suffix)

				if emoji is None:continue

				await message.add_reaction(emoji)
			