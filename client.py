import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from dizexrt import MyContext, MessageTools
from dizexrt.voice import PlayerManger

class MyClient(commands.Bot):

    def __init__(self, *, token_key = None, token = None) -> commands.Bot:
        prefix = commands.when_mentioned_or('d.')
        options = {}
        options['intents'] = discord.Intents.all()
        super().__init__(prefix, help_command=None, description=None, **options)
        self.tools = MessageTools(self)
        self.voice = PlayerManger(self)
        self.token_key = token_key
        self.token = token
    
    message_tasks = {}

    def add_message_task(self, task, guild):
        try:
            self.message_tasks[str(guild.id)]
        except:
            self.message_tasks[str(guild.id)] = []
        finally:
            self.message_tasks[str(guild.id)].append(task)
    
    async def run_message_task(self, message):
        try:
            self.message_tasks[str(message.guild.id)]
        except:
            return
        else:
            guild_tasks = self.message_tasks[str(message.guild.id)]
        for task in guild_tasks:
            await task(self, message)
    
    async def on_ready(self):
        print (f'loged in as {self.user.name}')
        await self.change_presence(activity = discord.Activity(type = discord.ActivityType.listening, name = "Your hearth"), status = discord.Status.idle)

    async def get_context(self, message, *, cls=MyContext):
        return await super().get_context(message, cls=cls)

    def load_extension_folder(self, name, *, ignore_package:list = []):
        cog_path = '.'.join(name.split('/'))
        packages = [f'{cog_path}.{package[:-3]}' for package in os.listdir(name) if package.endswith('.py') and package[:-3] not in ignore_package]
        for package in packages:self.load_extension(package) 
    
    def run(self, *, token = None):
        if token is None:
            if self.token is not None:
                token = self.token
            else:
                token = os.environ[self.token_key]
        return super().run(token)

    def run_env(self):
        load_dotenv()
        token = os.getenv('TOKEN')
        return super().run(token)