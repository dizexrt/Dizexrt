import discord

class UrlButton(discord.ui.View):
    def __init__(self, url:str):
        super().__init__(timeout = None)
        self.add_item(discord.ui.Button(label="link", url=url))

class Queue(discord.ui.View):
    def __init__(self, client):
        super().__init__(timeout = None)
        self.client = client
    
    @discord.ui.button(label = 'close', custom_id = 'queue:close', style = discord.ButtonStyle.danger)
    async def close(self, button, interaction:discord.Interaction):
        if interaction.user.voice is not None and interaction.user.voice.channel == interaction.guild.voice_client.channel:
            return await interaction.message.delete()
        return await interaction.response.send_message("You do not have permission to do this.", ephemeral=True)
    
    @discord.ui.button(label = 'edit', custom_id = 'queue:edit', style = discord.ButtonStyle.success)
    async def edit(self, button, interaction:discord.Interaction):
        if interaction.user.voice is not None and interaction.user.voice.channel == interaction.guild.voice_client.channel:
            queue = self.client.voice.get_queue(interaction.guild)
            for i in range(len(queue)):
                fmt = f'```\n{i+1} {queue[i].title}\n```'
                message = await interaction.channel.send(fmt)
                await message.add_reaction('✖')
            return
        return await interaction.response.send_message("You do not have permission to do this.", ephemeral=True)

class MusicButton(discord.ui.View):
    def __init__(self, client, url, *, timeout = None, loop:bool = False, loop_all:bool = False, close = False):
        super().__init__(timeout = timeout)
        self.client = client
        self.children[2].style = discord.ButtonStyle.success if loop else discord.ButtonStyle.gray
        self.children[3].style = discord.ButtonStyle.success if loop_all else discord.ButtonStyle.gray
        self.add_item(discord.ui.Button(label="link", url=url, row =1))

        if close:
            for item in self.children:
                item.disabled = True

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
            switch = 'on' if loop else 'off'
            return await interaction.response.send_message(f"`{interaction.user.display_name}` has turned {switch} loop current song")

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
            switch = 'on' if loop else 'off'
            return await interaction.response.send_message(f"`{interaction.user.display_name}` has turned {switch} loop all song.")
    
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
            
            await interaction.response.send_message(embed = embed, view = Queue(self.client))
