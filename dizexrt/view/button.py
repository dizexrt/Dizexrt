import discord

class UrlButton(discord.ui.View):
    def __init__(self, url:str):
        super().__init__()
        self.add_item(discord.ui.Button(label="link", url=url))

class EmbedClose(discord.ui.View):
    def __init__(self, user):
        super().__init__()
        self.add_item(CloseButton(user))

class CloseButton(discord.ui.Button):
    def __init__(self, user):
        super().__init__(label = 'close', custom_id = 'embed:close', style = discord.ButtonStyle.danger)
        self.user_id = [_.id for _ in user]
        self.user = user
    
    async def callback(self, interaction:discord.Interaction):
        if interaction.user.id not in self.user_id:
            return await interaction.response.send_message("You do not have permission to do this.", ephemeral=True)
        else:
            await interaction.message.delete()

class MusicButton(discord.ui.View):
    def __init__(self, client, url, *, timeout = None, loop:bool = False, loop_all:bool = False):
        super().__init__(timeout = timeout)
        self.client = client
        self.children[2].style = discord.ButtonStyle.success if loop else discord.ButtonStyle.gray
        self.children[3].style = discord.ButtonStyle.success if loop_all else discord.ButtonStyle.gray
        self.add_item(discord.ui.Button(label="link", url=url, row =1))

    async def on_timeout(self, item, interaction):
        return self.clear_items()
    
    @discord.ui.button(emoji = '⏹', custom_id = 'music:stop', style = discord.ButtonStyle.danger)
    async def stop_music(self, button, interaction:discord.Interaction):

        if interaction.user.voice is None:
            return await interaction.response.send_message("You have to join voice channel first.", ephemeral=True)
        
        if interaction.guild.voice_client is None:
            return await interaction.response.send_message("Bot is not in voice channel now.", ephemeral=True)

        if interaction.user.voice.channel != interaction.guild.voice_client.channel:
            return await interaction.response.send_message("You have to join bot's voice channel first.", ephemeral=True)
        
        if interaction.user.voice.channel == interaction.guild.voice_client.channel:
            await self.client.voice.stop(interaction.guild)
            return await interaction.response.send_message(f"`{interaction.user.display_name}` has disconnected bot from voice channel.")
    
    @discord.ui.button(emoji = '⏭', custom_id = 'music:skip', style = discord.ButtonStyle.secondary)
    async def skip_music(self, button, interaction:discord.Interaction):

        if interaction.user.voice is None:
            return await interaction.response.send_message("You have to join voice channel first.", ephemeral=True)
        
        if interaction.guild.voice_client is None:
            return await interaction.response.send_message("Bot is not in voice channel now.", ephemeral=True)

        if interaction.user.voice.channel != interaction.guild.voice_client.channel:
            return await interaction.response.send_message("You have to join bot's voice channel first.", ephemeral=True)
        
        if interaction.user.voice.channel == interaction.guild.voice_client.channel:
            await self.client.voice.skip(interaction.guild)
            return await interaction.response.send_message(f"`{interaction.user.display_name}` has skipped the song.")
    
    @discord.ui.button(emoji = '🔂', custom_id = 'music:loop', style = discord.ButtonStyle.secondary)
    async def loop_music(self, button, interaction:discord.Interaction):

        if interaction.user.voice is None:
            return await interaction.response.send_message("You have to join voice channel first.", ephemeral=True)
        
        if interaction.guild.voice_client is None:
            return await interaction.response.send_message("Bot is not in voice channel now.", ephemeral=True)

        if interaction.user.voice.channel != interaction.guild.voice_client.channel:
            return await interaction.response.send_message("You have to join bot's voice channel first.", ephemeral=True)
        
        if interaction.user.voice.channel == interaction.guild.voice_client.channel:
            loop = self.client.voice.loop(interaction.guild)
            self.children[2].style = discord.ButtonStyle.success if loop else discord.ButtonStyle.gray
            self.children[3].style = discord.ButtonStyle.gray if loop else self.children[3].style
            await interaction.message.edit(view = self)
            return await interaction.response.send_message(f"`{interaction.user.display_name}` has looped current song")

    @discord.ui.button(emoji = '🔁', custom_id = 'music:loop_all', style = discord.ButtonStyle.secondary)
    async def loop_all_music(self, button, interaction:discord.Interaction):

        if interaction.user.voice is None:
            return await interaction.response.send_message("You have to join voice channel first.", ephemeral=True)
        
        if interaction.guild.voice_client is None:
            return await interaction.response.send_message("Bot is not in voice channel now.", ephemeral=True)

        if interaction.user.voice.channel != interaction.guild.voice_client.channel:
            return await interaction.response.send_message("You have to join bot's voice channel first.", ephemeral=True)
        
        if interaction.user.voice.channel == interaction.guild.voice_client.channel:
            loop = self.client.voice.loop_all(interaction.guild)
            self.children[3].style = discord.ButtonStyle.success if loop else discord.ButtonStyle.gray
            self.children[2].style = discord.ButtonStyle.gray if loop else self.children[2].style
            await interaction.message.edit(view = self)
            return await interaction.response.send_message(f"`{interaction.user.display_name}` has looped all song.")
    
    @discord.ui.button(label = 'queue', custom_id = 'music:Queue', style = discord.ButtonStyle.primary, row = 1)
    async def url_music(self, button, interaction:discord.Interaction):

        if interaction.user.voice is None:
            return await interaction.response.send_message("You have to join voice channel first.", ephemeral=True)
        
        if interaction.guild.voice_client is None:
            return await interaction.response.send_message("Bot is not in voice channel now.", ephemeral=True)

        if interaction.user.voice.channel != interaction.guild.voice_client.channel:
            return await interaction.response.send_message("You have to join bot's voice channel first.", ephemeral=True)
        
        if interaction.user.voice.channel == interaction.guild.voice_client.channel:
            queue = self.client.voice.get_queue(interaction.guild)
            if queue is None:
                return await interaction.response.send_message('There are currently no more queued songs')
            
            fmt = "```\n"
            for i in range(len(queue)):
                fmt += f'{i+1} {queue[i].title}\n'
            fmt += '\n```'
            embed = discord.Embed(title=f'Upcoming - Next {len(queue)}', description=fmt, colour = discord.Colour.blue())
            embed.set_author(name = 'Queue')
            await interaction.response.send_message(embed = embed, view = EmbedClose(interaction.guild.voice_client.channel.members))
    
    