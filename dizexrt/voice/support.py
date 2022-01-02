import discord

class _BaseButton(discord.ui.Button):

    async def task(self, interaction):
        pass
    
    async def callback(self, interaction):
        if interaction.user.voice is None:
            return await interaction.channel.send("You have to join voice channel first.")
        
        if interaction.guild.voice_client is None:
            return await interaction.channel.send("Bot is not in voice channel now.")

        if interaction.user.voice.channel != interaction.guild.voice_client.channel:
            return await interaction.channel.send("You have to join bot's voice channel first.")
        
        if interaction.user.voice.channel == interaction.guild.voice_client.channel:
            await self.task(interaction)

class _BaseQueue(_BaseButton):

    def __init__(self, label):
        super().__init__(style = discord.ButtonStyle.primary, label = label)
    
    async def callback(self, interaction):
        await self.task(interaction)

class Previous(_BaseQueue):

    def __init__(self, queue, base):
        super().__init__('previous')
        self.queue = queue
        self.base = base
    
    async def task(self, interaction):
        self.queue.previous()
        await self.base.update()

class Next(_BaseQueue):

    def __init__(self, queue, base):
        super().__init__('next')
        self.queue = queue
        self.base = base
    
    async def task(self, interaction):
        self.queue.next()
        await self.base.update()

class QueueButton(discord.ui.View):
    
    def __init__(self, queue, base):
        super().__init__(timeout = None)
        self.add_item(Previous(queue, base))
        self.add_item(discord.ui.Button(label = f'Page : {queue.current+1}/{queue.max}', disabled = True))
        self.add_item(Next(queue, base))

class QueueEmbed(discord.Embed):

    def __init__(self, client, guild):
        super().__init__()
        self.title = "📋 Music Queue"
        self.client = client
        self.guild = guild
        self.colour = discord.Colour.blue()
        self.current = 0
    
    def default(self):
        self.add_field('Page : 1', value = 'No song in queue')
        return self
    
    @property
    def max(self):
        if self.queue is None or len(self.queue) == 0: return 1
        return len(self.queue)

    @property
    def queue(self):
        queue = self.client.voice.get_queue(self.guild)
        if queue is None: return []
        return queue
    
    def add_field(self, name, value):
        value = f"```\n{value}\n```"
        super().add_field(name = name, value = value, inline = False)
    
    def get_page(self, page:int) -> list:

        length = len(self.queue)

        if length == 0:return None

        pages = [p*10 for p in range(int(length/10)+1)]

        if page < len(pages) -1 :
            queue = self.queue[pages[page]:pages[page+1]]
        else:
            queue = self.queue[pages[page]:]
        
        return [_.title for _ in queue]

    def update(self):
        page = self.get_page(self.current)
        if page is None:
            data = "No song in queue"
        else:
            data = '\n'.join(page)
        self.add_field(name = f"Page : {self.current + 1}", value = data)
        return self

    def next(self):
        self.current += 1
        if self.current == len(self.queue):
            self.current = 0
        return self.update()
    
    def previous(self):
        self.current -= 1
        if self.current < 0:
            self.current = len(self.queue)-1
        return self.update()

class Queue:

    def __init__(self, bot, message):
        self.message = message
        self.bot = bot
        self.guild = message.guild
    
    @property
    def queue(self):
        return QueueEmbed(self.bot, self.guild)

    async def update(self):
        await self.message.edit(embed = self.queue.update(), view = QueueButton(self.queue, self))
    
    async def empty(self):
        await self.message.edit(embed = self.queue.default(), view = QueueButton(self.queue, self))

class PlayerEmbed(discord.Embed):

    def __init__(self):
        super().__init__()
        self.title = '▶ Music player'
        self.colour = discord.Colour.purple()
    
    @classmethod
    def extract_default(cls, guild):
        cls = cls()
        cls.add_field('Empty', 'No current song you can put url or song keywords from Youtube to this channel.')
        cls.set_thumbnail(url = guild.icon.url)
        cls.set_footer(text = f'server | {guild.name}')
        return cls
    
    @classmethod
    def extract_source(cls, source):
        cls = cls()
        cls.add_field('Title', source.title)
        cls.add_field('Channel', source.channel)
        cls.add_field('Duration', source.format_duration)
        cls.set_image(url = source.thumbnail)
        cls.set_footer(text = f'requester | {source.author}')
        return cls

    def add_field(self, name, value):
        value = f"```\n{value}\n```"
        super().add_field(name = name, value = value, inline = False)

class Stop(_BaseButton):
    def __init__(self, base, disabled, guild, client):
        self.guild = guild
        self.voice = client.voice
        self.base = base
        super().__init__(style = discord.ButtonStyle.danger, emoji = '⏹', disabled = disabled)

    async def task(self, interaction):
        await self.voice.stop(self.guild)

class Skip(_BaseButton):
    def __init__(self, base, disabled, guild, client):
        self.guild = guild
        self.voice = client.voice
        self.base = base
        super().__init__(emoji = '⏭', disabled = disabled)

    async def task(self, interaction):
        await self.voice.skip(self.guild)

class Loop(_BaseButton):
    def __init__(self, base, disabled, guild, client, source, on:bool = False):
        self.guild = guild
        self.voice = client.voice
        self.base = base
        self.source = source
        style = discord.ButtonStyle.success if on else discord.ButtonStyle.secondary
        super().__init__(emoji = '🔂', disabled = disabled, style = style)

    async def task(self, interaction):
        loop = self.voice.loop(self.guild)
        await self.base.loop(self.source, loop)

class LoopAll(_BaseButton):
    def __init__(self, base, disabled, guild, client, source, on:bool = False):
        self.guild = guild
        self.voice = client.voice
        self.base = base
        self.source = source
        style = discord.ButtonStyle.success if on else discord.ButtonStyle.secondary
        super().__init__(emoji = '🔁', disabled = disabled, style = style)

    async def task(self, interaction):
        loop = self.voice.loop_all(self.guild)
        await self.base.loop_all(self.source, loop)

class PlayerButton(discord.ui.View):

    def __init__(self, base, client, guild, loop, loop_all, source = None):
        self.guild = guild

        if source is None:
            self.disabled = True
            self.url = 'https://www.youtube.com/'
        else:
            self.disabled = False
            self.url = source.url

        super().__init__(timeout =None)

        self.add_item(Stop(base, self.disabled, self.guild, client))
        self.add_item(Skip(base, self.disabled, self.guild, client))
        self.add_item(Loop(base, self.disabled, self.guild, client, source, on = loop))
        self.add_item(LoopAll(base, self.disabled, self.guild, client, source, on = loop_all))
        self.add_item(discord.ui.Button(label = 'url', url = self.url))

class Player:

    def __init__(self, client, message):
        self.message = message
        self.guild = message.guild
        self.client = client
    
    @property
    def player(self):
        return PlayerEmbed
    
    async def loop(self, source, loop):
        loop_all = False
        await self.message.edit(embed = self.player.extract_source(source), view = PlayerButton(self, self.client, self.guild, loop, loop_all, source))
    
    async def loop_all(self, source, loop):
        loop_all = loop
        loop = False
        await self.message.edit(embed = self.player.extract_source(source), view = PlayerButton(self, self.client, self.guild, loop, loop_all, source))
    
    async def update(self, source, loop, loop_all):
        await self.message.edit(embed = self.player.extract_source(source), view = PlayerButton(self, self.client, self.guild, loop, loop_all, source))
    
    async def empty(self):
        await self.message.edit(embed = self.player.extract_default(self.guild), view = PlayerButton(self, self.client, self.guild, False, False))