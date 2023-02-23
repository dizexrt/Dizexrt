import discord
import os

from dotenv import load_dotenv

from discord.ext import commands
from bot.utils import MyContext

class MyClient(commands.Bot):

    def __init__(self, *, token_key:str = None) -> commands.Bot:
        prefix = commands.when_mentioned_or('d.')
        options = {}
        options['intents'] = discord.Intents.all()
        super().__init__(prefix, help_command=None, description=None, **options)
        self.token_key = token_key
    
    async def on_ready(
        self, *, 
        listenning_to : str = "Music",
        status : discord.Status
    ):
        print (f'loged in as {self.user.name}')
        await self.change_presence(
            activity = discord.Activity(
                type = discord.ActivityType.listening, 
                name = listenning_to
            ),
            status = status
        )

    async def get_context(self, message, *, cls=MyContext):
        return await super().get_context(message, cls=cls)

    def load_extension_folder(self, name, *, ignore_package:list = []):
        cog_path = '.'.join(name.split('/'))
        packages = [f'{cog_path}.{package[:-3]}' for package in os.listdir(name) if package.endswith('.py') and package[:-3] not in ignore_package]
        for package in packages:self.load_extension(package) 
    
    def run(self, *, token:str = None):
        try:
            token = os.environ[self.token_key]
        except:
            token = token
        finally:
            return super().run(token)

    def run_env(self, key:str):
        load_dotenv()
        token = os.getenv(key)
        return super().run(token)