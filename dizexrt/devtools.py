import discord
from .view import button, ButtonGroup

class MessageTools:

	def __init__(self, client):
		self.client = client
		self.url = UrlManager(client)
		self.file = FileManager(client)

	async def recognizes(self, message):
		message = Recognize(message)

		if message.is_url() and message.is_embed():
			await self.url.extract_domain(message)
			await message.delete()
			return

		if message.is_file():
			await self.file.recognizes(message)
			return

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

	def __init__(self, client):
		self.client = client
	
	async def get_emoji(self, guild, iter):
		emojis = [emoji.name for emoji in guild.emojis if emoji.name not in iter]
		
		if len(emojis) == 0: return

		for emoji in emojis:
			path = f'dizexrt/emojis/{emoji}.png'
			
			with open(path, "rb") as imageFile:
				image = imageFile.read()

			await guild.create_custom_emoji(name = emoji, image = image)
		
	def get(self, guild, find):
		for emoji in guild.emojis:
			if emoji.name == find:
				return emoji
		return None

class UrlManager(_Base):

	domains = ['github']

	def is_domain(self, url):
		for domain in self.domains:
			if domain in url:
				return True
		return False
	
	def domain(self, url):
		for domain in self.domains:
			if domain in url:
				return domain
		return None
	
	async def extract_domain(self, message):
		embed = message.embeds[0]
		embed.colour = discord.Colour.purple()
		url_button = ButtonGroup(
			button(on = True, label = 'link', style = 'link', url = embed.url)
		)
		message = await message.channel.send(embed = embed, components = url_button)

		if self.is_domain(embed.url):
			domain = self.domain(embed.url)
			emoji = self.get(message.guild, domain)

			if emoji is None:
				await self.get_emoji(message.guild, self.domains)

			await message.add_reaction(emoji)
	
class FileManager(_Base):

	file_types = ['py', 'cs', 'txt', 'docx']
	
	async def recognizes(self, message:discord.Message):

		if len(message.attachments) > 0:

			types = []

			for file in message.attachments:
				suffix = file.filename.split('.')[1]
				types.append(suffix)

			for suffix in types:
				if suffix in self.file_types:
					emoji = self.get(message.guild, suffix)

					if emoji is None:
						await self.get_emoji(message.guild, self.file_types)

					await message.add_reaction(emoji)
			
