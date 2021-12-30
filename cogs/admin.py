import discord
import dizexrt
from discord.ext import commands
from discord.commands import Option, SlashCommandGroup

class Setup(commands.Cog):

    def __init__(self, client):
        self.client = client

    setup = SlashCommandGroup('setup', 'setup function')

    setup_channel_choices = ["state", "developer"]
    setup_channel_option = Option(str, "Choose which option do you want to setup", choices=setup_channel_choices)
    setup_channel_id = Option(discord.TextChannel, 'select channel', required = False, default = None)
    @setup.command(description = 'setup channel', guild_ids = [dizexrt.guild])
    async def channel(self, ctx, option:setup_channel_option, channel:setup_channel_id):
        await ctx.respond(f"{option}{channel}")

def setup(client):
    client.add_cog(Setup(client))