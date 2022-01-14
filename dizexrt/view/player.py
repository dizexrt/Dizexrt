import discord
from .queue import QueueView

class MusicButton(discord.ui.Button):

    def __init__(self, task, **kwargs):

        #setup task for run
        self._task = task

        #get value from attribute **kwargs
        label       = kwargs.setdefault('label', None)
        emoji       = kwargs.setdefault('emoji', None)
        style       = kwargs.setdefault('style', None)
        disabled    = kwargs.setdefault('disabled', None)
        custom_id   = kwargs.setdefault('custom_id', None)
        url         = kwargs.setdefault('url', None)
        row         = kwargs.setdefault('row', None)

        #__init__ super class
        super().__init__(

            label       = label, 
            style       = style, 
            disabled    = disabled, 
            custom_id   = custom_id,
            url         = url, 
            emoji       = emoji, 
            row         = row

        )

    #when button is clicked
    async def callback(self, interaction):
        return await self._task(interaction)

    #create function for check permission
    @staticmethod
    def task(coro):

        #return function
        async def to_run(self, interaction):

            if interaction.user.voice is None:
                return await interaction.response.send_message("You have to join voice channel first.", ephemeral=True)
            
            if interaction.guild.voice_client is None:
                return await interaction.response.send_message("Bot is not in voice channel now.", ephemeral=True)

            if interaction.user.voice.channel != interaction.guild.voice_client.channel:
                return await interaction.response.send_message("You have to join bot's voice channel first.", ephemeral=True)
            
            if interaction.user.voice.channel == interaction.guild.voice_client.channel:
                #where coro run
                return await coro(self, interaction)

        return to_run

class MusicView(discord.ui.View):

    def __init__(
        self, 
        client, 
        url, 
        *, 
        timeout = None, 
        loop:bool = False, 
        loop_all:bool = False, 
        close = False
    ):
        self.client = client
        
        #__init__ super class
        super().__init__(timeout = timeout)

        #check style
        loop_style = discord.ButtonStyle.success if loop else discord.ButtonStyle.gray
        loop_all_style = discord.ButtonStyle.success if loop_all else discord.ButtonStyle.gray
        
        #create items
        items = [
            MusicButton(
                self.stop_music, 
                emoji = '⏹', 
                custom_id = 'music:stop', 
                style = discord.ButtonStyle.danger
            ),
            MusicButton(
                self.skip_music, 
                emoji = '⏭', 
                custom_id = 'music:skip', 
                style = discord.ButtonStyle.secondary
            ),
            MusicButton(
                self.loop_music,
                emoji = '🔂', 
                custom_id = 'music:loop', 
                style = loop_style
            ),
            MusicButton(
                self.loop_all_music, 
                emoji = '🔁', 
                custom_id = 'music:loop_all', 
                style = loop_all_style
            ),
            MusicButton(
                self.queue_music, 
                label = 'queue', 
                custom_id = 'music:Queue', 
                style = discord.ButtonStyle.primary, 
                row = 1
            ),
            discord.ui.Button(
                label = 'link', 
                url = url, 
                row = 1
            )
        ]

        #add itmes
        self.add_item(items[0])
        self.add_item(items[1])
        self.add_item(items[2])
        self.add_item(items[3])
        self.add_item(items[4])
        self.add_item(items[5])

        #if close button on
        if close:
            for item in self.children:
                item.disabled = True

    #when time out
    async def on_timeout(self, item, interaction):
        return self.clear_items()
    
    @MusicButton.task
    async def stop_music(self, interaction):
        await self.client.voice.stop(interaction.guild)
        return await interaction.response.send_message(f"`{interaction.user.display_name}` has disconnected bot from voice channel.")
    
    @MusicButton.task
    async def skip_music(self, interaction):
        await self.client.voice.skip(interaction.guild)
        return await interaction.response.send_message(f"`{interaction.user.display_name}` has skipped the song.")
    
    @MusicButton.task
    async def loop_music(self, interaction):
        loop = self.client.voice.loop(interaction.guild)

        self.children[2].style = discord.ButtonStyle.success if loop else discord.ButtonStyle.gray
        self.children[3].style = discord.ButtonStyle.gray if loop else self.children[3].style

        await interaction.message.edit(view = self)

        switch = 'on' if loop else 'off'

        return await interaction.response.send_message(f"`{interaction.user.display_name}` has turned {switch} loop current song")

    @MusicButton.task
    async def loop_all_music(self, interaction):
        loop = self.client.voice.loop_all(interaction.guild)

        self.children[3].style = discord.ButtonStyle.success if loop else discord.ButtonStyle.gray
        self.children[2].style = discord.ButtonStyle.gray if loop else self.children[2].style

        await interaction.message.edit(view = self)

        switch = 'on' if loop else 'off'

        return await interaction.response.send_message(f"`{interaction.user.display_name}` has turned {switch} loop all song.")
    
    @MusicButton.task
    async def queue_music(self, interaction):
        queue = self.client.voice.get_queue(interaction.guild)
        if queue is None:
            return await interaction.response.send_message('There are currently no more queued songs')
            
        await interaction.response.send_message(embed = self.client.voice.fqueue(interaction.guild), view = QueueView(self.client))