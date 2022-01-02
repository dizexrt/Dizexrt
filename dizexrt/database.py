from replit import db

class Database:

    @staticmethod
    def get(guild, item:str):
        try:
            value = db[str(guild.id)][item]
        except:
            value = None
        
        return value
    
    @staticmethod
    def set(guild, item:str, value):
        try:
            db[str(guild.id)]
        except:
            db[str(guild.id)] = {}
        
        db[str(guild.id)][item] = value
        return value
    
    @staticmethod
    def delete(guild, item:str):
        try:
            db[str(guild.id)][item]
        except:
            pass
        else:
            del db[str(guild.id)][item]