import os
from dizexrt import MyClient

token = os.environ['token']

client = MyClient()
client.load_extension_folder('cogs')

client.run(token)