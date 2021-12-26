import os
from dotenv import load_dotenv
from dizexrt import MyClient

load_dotenv()
token = os.getenv("TOKEN")

client = MyClient()
client.load_extension_folder('cogs')

client.run(token)