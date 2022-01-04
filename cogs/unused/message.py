from discord.ext import commands

class Message(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        await self.client.run_message_task(message)

def setup(client):

    client.add_cog(Message(client))