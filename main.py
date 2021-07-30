import discord
import config

from character import Character

client = discord.Client()

@client.event
async def on_ready():
    print('Bot successfully logged in as: {user}'.format(user=client.user))

@client.event
async def on_message(message):
    if message.content.startswith("$"):
        print(message)

    content = message.content
    channel = message.channel

    if content.startswith("$create"):
        content = content.replace("$create ", "")
        if content == "":
            content = "New Guy"

        new_guy = Character(content)
        new_guy.generate_characteristics(0)

        await channel.send(new_guy.print_stats())
    
    if content.startswith("$exterminatus"):
        await channel.purge()
        await channel.send("*The channel has been purged.*")


client.run(config.bot_token)