import discord
from discord import message
import config

client = discord.Client()

@client.event
async def on_ready():
    print('Bot successfully logged in as: {user}'.format(user=client.user))
async def on_message(message):
    if not message.content.startswith("$"):
        print(message)

client.run(config.bot_token)