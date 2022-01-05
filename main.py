from client import MyClient
from online import keep_alive

client = MyClient(token_key = 'dizexrt')
client.load_extension_folder('cogs')
client.load_extension('dizexrt.voice.player')


keep_alive()
client.run()