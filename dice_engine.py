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
        character_check = re.compile("[0-9|d|+|-]*")
        if not character_check.fullmatch(command):
            raise ValueError("Illegal characters")

        # Check that all 'd' terms have nonzero adjacent numbers
        zero_rolls_check = re.compile("(^0|[+]0|-0)d")
        d_zeroes_check = re.compile("d(0$|0[+]|0-)")

        if zero_rolls_check.search(command) or d_zeroes_check.search(command):
            raise ValueError("Dices rolls must have positive values!")

        return command

    # given a string of the form [num]d[num], rolls appropriately
    # mode is 1 for addition and -1 for subtraction
    # roll_results is a reference to a list of roll results
    def ndn_roll(self, roll_code, mode, roll_results):
        if roll_code.startswith("d"):
            roll_code = "1" + roll_code
        roll = roll_code.split("d")

        if int(roll[0]) > 0 and int(roll[1]) > 0:
            rolls_completed = 0

            # Roll the specified number of times
            while rolls_completed < int(roll[0]):
                result = randrange(1, int(roll[1])+1)
                roll_results.append(result * mode)
                rolls_completed += 1
        else:
            raise ValueError("Can't roll 0 dice or d0s")
        return 

    async def parse_roll_term(self, term, mode, roll_results, channel):

        if "d" in term:
            try:
                self.ndn_roll(term, mode, roll_results)
                return 0
            except ValueError:
                await channel.send("Treason!  Dice terms must have both a number of rolls and a number of sides!")
        else:
            return int(term) * mode

    async def parse_command(self, command, channel):

        try:
            command = self.sanitize_command(command)
        except TypeError:
            await channel.send("Heresy! Empty roll command!")
            return
        except ValueError:
            await channel.send("Missing or heretical characters in roll command!")
            return

        # Sanitizing ensures there are no characters but numbers, operators, and "d"

        dice_results = []
        total = 0

        command = command.split("+")

        for top_term in command:

            # first check if there are subtraction terms to split off
            try:
                if "-" in top_term:
                    top_term = top_term.split("-")

                    index = len(top_term) - 1

                    # add first term
                    total += await self.parse_roll_term(top_term[0],1,dice_results, channel)

                    # subtract the rest
                    while index > 0:

                        total += await self.parse_roll_term(top_term[index],-1,dice_results, channel)
                        index -= 1

                else: # if not, add this term and we're done
                    total += await self.parse_roll_term(top_term,1,dice_results, channel)
            except TypeError:
                return

        # set up output
        output_str = "**Roll result:** \n **]|[**"

        if dice_results:
            for result in dice_results:
                total += result
                output_str += " {},".format(result)

                # Delete the comma at the end of the list
                output_str = output_str[:-1]

        output_str += " **]|[**\n**Total:** {}".format(total)

        await channel.send(output_str)
        return