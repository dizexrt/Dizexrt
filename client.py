import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from dizexrt import MyContext, MessageTools
from dizexrt.voice import PlayerManger

class MyClient(commands.Bot):

    def __init__(self) -> commands.Bot:
        prefix = commands.when_mentioned_or('d.')
        options = {}
        options['intents'] = discord.Intents.all()
        super().__init__(prefix, help_command=None, description=None, **options)
        self.tools = MessageTools(self)
        self.voice = PlayerManger(self)
    
    async def on_ready(self):
        print (f'loged in as {self.user.name}')
        await self.change_presence(activity = discord.Game('ใ จ เ ก เ ร'), status = discord.Status.idle)

    async def get_context(self, message, *, cls=MyContext):
        return await super().get_context(message, cls=cls)

    def load_extension_folder(self, name):
        cog_path = '.'.join(name.split('/'))
        packages = [f'{cog_path}.{package[:-3]}' for package in os.listdir(name) if package.endswith('.py')]
        for package in packages:self.load_extension(package) 
    
    def run(self):
        token = os.environ['saiimaih']
        return super().run(token)

    def run_env(self):
        load_dotenv()
        token = os.getenv('TOKEN')
        return super().run(token)