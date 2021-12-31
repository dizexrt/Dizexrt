from discord.commands import user_command
from discord.ext import commands
import discord

class UserCommand(commands.Cog):

    def __init__(self, client):
        self.client = client

    @user_command(name = 'givelove', default_permission = False)
    async def love(self, ctx,  user:discord.Member):
        
        if user.bot:
            return await ctx.respond(f'จะบอกรักบอททำไม บอกไปบอทจะรับรู้หรอ', ephemeral=True)

        if user.dm_channel is None:
            await user.create_dm()
        try:
            await user.dm_channel.send('มีใครบางคนกำลังแอบบอกรักแกอยู่นะ')
        except:
            return await ctx.respond(f'ไม่มีสิทธิ์ส่งคำว่ารักให้ไปถึง {user.name}', ephemeral=True)
        else:
            return await ctx.respond(f'กระซิบคำว่ารักไปถึง `{user.name}` แล้ว', ephemeral=True)

def setup(client):
    client.add_cog(UserCommand(client))

