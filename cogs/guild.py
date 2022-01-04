from discord.ext import commands
import dizexrt
import discord
import datetime

class Guild(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id != dizexrt.guild:return

        channel = await member.guild.fetch_channel(dizexrt.channels['member'])

        embed = discord.Embed()
        embed.title = 'Hello new user'
        embed.colour = discord.Colour.purple()
        embed.description = f'{member.mention}```\nwelcome to {member.guild} server\n```'
        embed.set_thumbnail(url = member.display_avatar.url)
        embed.add_field(name = 'Start time', value = f'```\n{(member.joined_at + datetime.timedelta(hours=7)).strftime("%c")}\n```', inline=False)

        await channel.send(embed = embed)
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.guild.id != dizexrt.guild:return

        channel = await member.guild.fetch_channel(dizexrt.channels['member'])

        embed = discord.Embed()
        embed.title = 'good bye user'
        embed.colour = discord.Colour.purple()
        embed.description = f'{member.mention}```\nthank you to join with us\n```'
        embed.set_thumbnail(url = member.display_avatar.url)
        embed.add_field(name = 'All time', value = f'```\n{days_from(member.joined_at)} days since {(member.joined_at + datetime.timedelta(hours=7)).strftime("%c")}\n```', inline = False)

        await channel.send(embed = embed)

def days_from(date:datetime.datetime):
    d1 = date.date()
    d2 = datetime.datetime.utcnow().date()
    return abs(d2 - d1).days

def setup(client):
    client.add_cog(Guild(client))