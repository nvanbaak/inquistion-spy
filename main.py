import discord
import config

from character import Character
from state_manager import State_Manager

client = discord.Client()
sm = State_Manager()

@client.event
async def on_ready():
    print('Bot successfully logged in as: {user}'.format(user=client.user))

@client.event
async def on_message(message):
    if message.content.startswith("$"):
        print(message)
        await sm.handle_command(client, message)

client.run(config.bot_token)