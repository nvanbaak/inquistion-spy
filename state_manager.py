import os
from random import randrange
import discord
import config

from character import Character

class State_Manager:
    def __init__(self):

        # alias setup
        self.aliases = {}

        # load any existing aliases
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

        # load characters; slightly different process but follows the same logic as aliases
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
    async def handle_command(self, message):
        
        content = message.content
        channel = message.channel

        if content.startswith("$create"):
            content = content.replace("$create ", "")
            if content == "":
                content = "New Guy"

            new_guy = Character(content)
            new_guy.generate_characteristics(0)

            await channel.send(new_guy.print_stats())

        elif content.startswith("$roll"):

            # Remove command term
            content = content.replace("$roll ","")
            content = content.replace("$roll","")

            # Expunge spaces around operators
            content = content.replace(" + ","+")
            content = content.replace(" +","+")
            content = content.replace("+ ","+")

            content = content.replace(" - ","-")
            content = content.replace(" -","-")
            content = content.replace("- ","-")

            content = content.split("+")

            dice_results = []
            total = 0

            for term in content:

                # if it's a constant, we just add it; else parse as die roll
                try:
                    total += int(term)
                except ValueError:

                    roll = term.split("d",1)

                    if len(roll) > 1:
                        rolls_completed = 0

                        # Check that inputs are valid
                        try:
                            int(roll[0])
                        except ValueError:
                            await channel.send("Heresy! '{}' is not a valid number of rolls!".format(roll[0]))
                            return
                        try:
                            int(roll[1])
                        except ValueError:
                            await channel.send("Heresy! '{}' is an invalid die type!".format(roll[1]))
                            return

                        # Roll the specified number of times
                        while rolls_completed < int(roll[0]):
                            result = randrange(1, int(roll[1])+1)
                            dice_results.append(result)
                            rolls_completed += 1

            output_str = "**Roll result:** \n **]|[**"

            for result in dice_results:
                total += result
                output_str += " {},".format(result)

            # Delete the comma at the end of the list
            output_str = output_str[:-1]
            output_str += " **]|[**\n**Total:** {}".format(total)

            await channel.send(output_str)
            return


        elif content.startswith("$exterminatus"):
            if message.author.id == config.admin_id:
                await channel.purge()
                await channel.send("*The channel has been purged.*")
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