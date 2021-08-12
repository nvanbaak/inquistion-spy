from datetime import time
import os
from posixpath import expanduser
from random import randrange
import discord
import re

import config
from dice_engine import Dice_Roller
from timezones import Time_Manager

from character import Character

class State_Manager:
    def __init__(self):

        # create instances of utility classes
        self.dice_roller = Dice_Roller()
        self.time_manager = Time_Manager()

        # define binary re
        self.binary_check = re.compile("[0|1| ]*")

        # load commendations
        self.commendations = {}
        if os.path.exists("commendations.txt"):
            with open("commendations.txt", "r", -1, "utf8") as commendation_list:
                purity_seals = commendation_list.read().split("\n")

                # last entry is empty, so we kill it
                del purity_seals[-1]

                # add up everyone's purity seals
                for seal in purity_seals:
                    seal = seal.split("&separator;")
                    if not seal[0] in self.commendations:
                        self.commendations[seal[0]] = 0
                    self.commendations[seal[0]] += int(seal[1])

            # add up everyone's totals and rewrite the file
            new_list = ""
            for person in self.commendations:
                new_list += "{}&separator;{}\n".format(person, self.commendations[person])

            with open("commendations.txt", "w", -1, "utf8") as cl:
                cl.write(new_list)

        # load aliases
        self.aliases = {}
        if os.path.exists("alias.txt"):
            with open("alias.txt", "r", -1, "utf8") as alias_list:
                alias_data = alias_list.read().split("\n")

                # delete the newline at the end
                del alias_data[-1]

                # add each alias to the state machine
                for alias in alias_data:
                    alias = alias.split("&separator;")
                    self.aliases[alias[0]] = alias[1]
                    print("{alias} alias = {nickname}".format(alias=alias[0],nickname=alias[1]))
                # note that this collapses duplicate entries to whatever the player entered last

                # save dict back to file (which removes duplicate entries)
                self.update_local_aliases()

        # load characters
        if os.path.exists("characters.txt"):
            with open("characters.txt", "r", -1, "utf8") as char_list:
                char_list = char_list.read().split("\n")

                # 

                return

    def update_local_aliases(self):

        # Make a string out of alias dict
        alias_str = ""
        for key in self.aliases:
            alias_str += "{account}&separator;{alias}\n".format(account=key, alias=self.aliases[key])

        # save to file
        with open("alias.txt","w",-1,"utf8") as alias_list:
            alias_list.write(alias_str)

        return "Updated alias list at alias.txt!"

    def save_cast(self):
        with open("characters.txt", "w", -1, "uft8") as char_database:
            char_database.write("Done!")
        
        return

    # Takes a command, parses it, does the appropriate thing
    async def handle_command(self, client, message):

        content = message.content
        channel = message.channel

        if self.binary_check.fullmatch(content):
            
            pass

        elif content.startswith("$create"):
            content = content.replace("$create ", "")
            if content == "":
                content = "New Guy"

            new_guy = Character(content, "bob")
            new_guy.generate_characteristics(0)

            await channel.send(new_guy.print_stats())

        elif content.startswith("$time"):
            content = content.replace("$time ", "")
            content = content.replace("$time", "")

            await self.time_manager.parse_command(content, channel)

        elif content.startswith("$roll"):

            # Remove command term
            content = content.replace("$roll ","")
            content = content.replace("$roll","")

            await self.dice_roller.parse_command(content,channel)
            return

        elif content.startswith("$exterminatus"):
            if message.author.id == config.admin_id:
                target_number = int(content.split(" ")[1]) + 1 # +1 to also delete the command
                if target_number:
                    await channel.purge(limit=target_number, check=self.return_true)
                    # await channel.send("*The heresy has been purged.*")
            else:
                await channel.send("That's heresy!")

        elif content.startswith('$register'):

            # retrieve Discord name and given name from message
            author_name = str(message.author.id)
            author_nickname = message.author.name
            content = content.replace("$register ","")
            content = content.replace("$register","")
            alias = content

            if alias:
                # set that value in the alias list
                self.aliases[author_name] = alias
                
                alias_str = "{author_name}&separator;{alias}\n".format(author_name=author_name, alias=alias)

                # save alias to alias list
                with open("alias.txt", "a", -1, "utf8") as alias_list:
                    alias_list.write(alias_str)

                # confirmation message
                await message.channel.send("Registered {author} as {alias}!".format(author=author_nickname, alias=alias))

            else:
                await message.channel.send("You need to provide a name to use that command.")

        elif content.startswith("$commend"):
            if message.author.id == config.admin_id:
                content = content.replace("$commend ", "").replace("$commend", "")

                with open("commendations.txt", "a", -1, "utf8") as commendations:

                    entry = "{}&separator;{}\n".format(content,1)

                    commendations.write(entry)

                if not content in self.commendations:
                    self.commendations[content] = 1
                else:
                    self.commendations[content] += 1

                plural = "s"
                if self.commendations[content] == 1:
                    plural = ""

                await channel.send('I have awarded a purity seal to **{}** for their service to the Emperor!  {} has **{}** purity seal{}.\n\nYou can view your purity seals with "$purity `your name`"'.format(content, content, self.commendations[content], plural))
            else:
                await channel.send("Heresy!  You do not have the authorization to award purity seals!")

        elif content.startswith("$purity"):
            content = content.replace("$purity ", "").replace("$purity", "")

            try:
                seals = self.commendations[content]
            except KeyError:
                await channel.send("{} does not have any purity seals.  Increase your devotion to the Emperor!").format(content)
                return
            
            await channel.send("The loyal servant of the Emperor **{}** has been graced with **{}** purity seals.  A great honor!".format(content, seals))


    def from_this_guy(self, message, target):
        return message.author == target
    
    def return_true(self, message):
        return True