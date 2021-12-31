from replit import db

class Database:

    @staticmethod
    def pull(guild, item:str):
        try:
            db[str(guild.id)]
        except:
            value = None
        else:
            value = db[str(guild.id)][item]
        
        return value
    
    @staticmethod
    def set(guild, item:str, value):
        try:
            db[str(guild.id)]
        except:
            db[str(guild.id)] = {}
        
        db[str(guild.id)][item] = value
        return value

class ChannelData:

    def __init__(self, channel, key):
        self.channel = channel
        self.guild = channel.guild
        self.key = key
    
    def set_message(self, key:str, message):
        Database.set(self.guild, f'{self.key}:{key}', message.id)
        return message
    
    async def fetch_message(self, key:str):
        message_id = Database.get(self.guild, f'{self.key}:{key}')
        try:
            message = await self.channel.fetch_message(message_id)
        except:
            message = None
           
        return message

class GuildData:

    def __init__(self, guild):
        self.guild = guild

    def get_channel(self, key:str):
        channel_id = Database.pull(self.guild, f'{key}:channel')
        try:
            base = self.guild.get_channel(channel_id)
            channel = ChannelData(base, key)
        except:
            channel = None
        return channel
    
    def set_channel(self, key:str, channel):
        Database.set(self.guild, f'{key}:channel', channel.id)
        return channel