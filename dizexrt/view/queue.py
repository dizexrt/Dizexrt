import discord

class QueueButton(discord.ui.Button):

    STYLE = {
        'GRAY':discord.ButtonStyle.secondary,
        'BLUE':discord.ButtonStyle.primary,
        'GREEN':discord.ButtonStyle.success,
        'RED':discord.ButtonStyle.danger,
    }

    def __init__(self, task, name, colour:str = 'gray'):
        self._task = task
        style = self.STYLE[colour.upper()]
        super().__init__(label = name, style = style)

    async def callback(self, interaction):
        return await self._task(interaction)

    @staticmethod
    def task(coro):
        async def to_run(self, interaction):
            if interaction.user.voice is not None and interaction.user.voice.channel == interaction.guild.voice_client.channel:
                return await coro(self, interaction)
            return await interaction.response.send_message("You do not have permission to do this.", ephemeral=True)
        return to_run

class QueueView(discord.ui.View):

    def __init__(self, client):
        super().__init__(timeout = None)
        self.client = client

        self.add_item(QueueButton(self.close, 'close', 'blue'))
        self.add_item(QueueButton(self.edit, 'edit', 'green'))
        self.add_item(QueueButton(self.clear, 'clear', 'red'))
    
    @QueueButton.task
    async def close(self, interaction):
        await interaction.message.delete()

    @QueueButton.task
    async def clear(self, interaction):
        await self.client.voice.clear_queue(interaction.guild)
        await interaction.message.delete()
        await interaction.channel.send(f'`{interaction.user}` has cleared queue')
        
    @QueueButton.task
    async def edit(self, interaction):
        await self.client.voice.edit_queue(interaction.channel)
        embed = self.client.voice.fqueue(interaction.guild)
        await interaction.response.send_message(content = 'edited!', embed = embed, view = self)
        