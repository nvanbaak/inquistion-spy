import discord
import config
import re

from character import Character
from utility.state_manager import State_Manager

client = discord.Client()
sm = State_Manager()

binary_check = re.compile("[0-1| ]*")

@client.event
async def on_ready():
    print('Bot successfully logged in as: {user}'.format(user=client.user))

@client.event
async def on_message(message):
    is_binary = binary_check.fullmatch(message.content)
    if message.content.startswith("$") or is_binary:
        print(message)
        await sm.handle_command(client, message, is_binary)

client.run(config.bot_token)