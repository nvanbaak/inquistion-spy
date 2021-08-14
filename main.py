import discord
import config
import re

from utility.state_manager import State_Manager

class MyClient(discord.Client):
    def __init__(self, *, loop=None, **options):
        super().__init__(loop=loop, **options)

        self.sm = State_Manager()

        self.binary_check = re.compile("[0-1| ]*")
        self.active_env = config.env
        self.muted = False
    
    async def on_ready(self):
        print('Bot successfully logged in as: {user}'.format(user=client.user))

    async def on_message(self, message):
        # this code lets us have multiple instances of the bot running, but choose which one responds for debugging purposes
        if message.content.startswith("$set env ") and message.author.id == config.admin_id:
            print(message.content)

            self.active_env = message.content.replace("$set env", "").replace(" ", "")

            # if we're already active:
            if not self.muted and self.active_env == config.env:
                await message.channel.send ("`{}` is already the active environment.".format(config.env))

            if not self.muted and self.active_env != config.env:
                await message.channel.send("- Muting `{}`.".format(config.env))
                self.muted = True

            elif self.muted and self.active_env == config.env:
                await message.channel.send("- Unmuting `{}`.".format(config.env))
                self.muted = False
            return

        if not self.muted:
            is_binary = self.binary_check.fullmatch(message.content)
            if message.content.startswith("$") or is_binary:
                print(message)
                await self.sm.handle_command(client, message, is_binary)


client = MyClient()
client.run(config.bot_token)