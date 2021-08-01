from random import randrange
import discord
import re

class Dice_Roller:
    def __init__(self):
        pass

    # Sanitizes dice input
    def sanitize_command(self, command):

        # Currently the '$roll' term is removed in the State Manager, so we assume it's gone by now 

        # Expunge spaces
        command = command.replace(" ","")

        if command == "":
            raise TypeError("Empty argument")

        # Check that no illegal characters are used
        result = re.compile("[0-9|d|+|-]*")
        if not result.fullmatch(command):
            raise ValueError("Illegal characters")

        return command

    # given a string of the form [num]d[num], rolls appropriately
    # mode is 1 for addition and -1 for subtraction
    # roll_results is a reference to a list of roll results
    def ndn_roll(self, roll_code, mode, roll_results):
        roll = roll_code.split("d",1)

        if len(roll) > 1:
            rolls_completed = 0

            # Roll the specified number of times
            while rolls_completed < int(roll[0]):
                result = randrange(1, int(roll[1])+1)
                roll_results.append(result * mode)
                rolls_completed += 1
        return 

    def parse_roll_term(self, term, mode, roll_results):

        if "d" in term:
            self.ndn_roll(term, mode, roll_results)
            return 0
        else:
            return int(term) * mode

    async def parse_command(self, channel, command):

        try:
            command = self.sanitize_command(command)
        except TypeError:
            await channel.send("Heresy! Empty roll command!")
            return
        except ValueError:
            await channel.send("Heresy! Illegal characters in roll command!")
            return

        # Sanitizing ensures there are no characters but numbers, operators, and "d"

        dice_results = []
        total = 0

        command = command.split("+")

        for top_term in command:

            # first check if there are subtraction terms to split off
            if "-" in top_term:
                top_term = top_term.split("-")

                index = len(top_term)

                # add first term
                total += self.parse_roll_term(top_term[0],1,dice_results)

                # subtract the rest
                while index > 0:

                    total += self.parse_roll_term(top_term[index],-1,dice_results)
                    index -= 1

            else: # if not, add this term and we're done
                total += self.parse_roll_term(top_term,1,dice_results)

        # set up output
        output_str = "**Roll result:** \n **]|[**"

        for result in dice_results:
            total += result
            output_str += " {},".format(result)

        # Delete the comma at the end of the list
        output_str = output_str[:-1]
        output_str += " **]|[**\n**Total:** {}".format(total)

        await channel.send(output_str)
        return