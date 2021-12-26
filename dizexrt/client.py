import discord
import os
from discord.ext.commands import Bot, Context
from .voices import Voice

def alert(message):
    embed = discord.Embed()
    embed .title = "📢 Bot Alert"
    embed.description = message
    return embed

class AlertContext(Context):

    async def alert(self, message):
        embed = alert(message)
        return await self.send(embed = embed)

class MyClient(Bot):

    def __init__(self):
        options = {}
        options['intents'] = discord.Intents.all()
        prefix = '-'
        super().__init__(command_prefix=prefix, **options)
        self.voice = Voice(self)

    async def get_context(self, message, *, cls=AlertContext):
        return await super().get_context(message, cls=cls)

    def load_extension_folder(self, folder_name:str):
        for file in os.listdir(folder_name):
            if file.endswith('.py'):
                self.load_extension(f'{folder_name}.{file[:-3]}')

    async def on_ready(self):
        print(f"Loged in as {self.user}")
        