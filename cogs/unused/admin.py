mport discord
import dizexrt
from discord.ext import commands
from discord.commands import Option, SlashCommandGroup

class Setup(commands.Cog):

    def __init__(self, client):
        self.client = client

    setup = SlashCommandGroup('setup', 'setup function')

    setup_channel_choices = ["music"]
    setup_channel_option = Option(str, "Choose type of channel that you want to create", choices=setup_channel_choices)
    setup_channel_id = Option(discord.TextChannel, "If you want to create new channel you don't have to select this.", required = False, default = None)
    @setup.command(description = 'Create channel')
    async def channel(self, ctx, option:setup_channel_option, channel:setup_channel_id):
        try:
            _channel = await ctx.guild.fetch_channel(dizexrt.db.get(ctx.guild))
        except:
            _channel = None

        if _channel is not None:
            return await ctx.respond(f"This channel of option is already exist {_channel.channel.mention}")

        if channel is None:
            try:
                channel = await ctx.guild.create_text_channel(f"{self.client.user.name} {option} room")
            except:
                return await ctx.respond(f"Bot is not have permission to set up channel")
        
        dizexrt.db.set(ctx.guild, f'{option}:channel', channel.id)
        await ctx.respond(f"Created setup channel as : {channel.mention}")
        
        if option == 'music':
            return await self.client.voice.setup_channel(channel)
        
        if option == 'file':
            if (ctx.guild.emoji_limit - len(ctx.guild.emojis)) < 5:
                pass
    
    @channel.before_invoke
    async def check_permission_author(self, ctx):
        for role in ctx.author.roles:
            if role.permissions.administrator:return
            if role.permissions.manage_channels:return
        
        await ctx.respond("You cannot use this command")
        raise commands.CommandError('Author have not permission')

def setup(client):
    client.add_cog(Setup(client))