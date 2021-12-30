import discord
from discord.ext import commands

class MyContext(commands.Context):

    async def alert(self, content, **kwargs):
        embed = discord.Embed(colour = discord.Color.purple(), description = content)
        embed.set_author(name = 'Noticefication', icon_url='https://discord.com/channels/871796847038066748/924966351192342538/924967169232629782')
        await self.send(embed = embed, **kwargs)
