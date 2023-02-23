from discord.ext.commands import Context

class SimpleContext(Context):

	async def send(self, content, *, embed:dict = {"name":None, "value":None}, **kwargs):
		super().send(content, **kwargs)