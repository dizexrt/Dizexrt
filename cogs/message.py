from discord.ext import commands
from discord.commands import message_command
import dizexrt

class Message(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.channel.id == dizexrt.channels['file']:
            return await self.client.tools.extract_file(message)
    
    @message_command()
    async def indentify(self, ctx, message):
        await self.client.tools.identify(message)
        await ctx.respond("This message was indentified", ephemeral=True)

def setup(client):

    client.add_cog(Message(client))