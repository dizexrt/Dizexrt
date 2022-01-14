import discord

class UrlButton(discord.ui.View):
    def __init__(self, url:str):
        super().__init__(timeout = None)
        self.add_item(discord.ui.Button(label="link", url=url))