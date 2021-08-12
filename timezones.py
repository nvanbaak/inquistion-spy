import re
import discord


class Time_Manager:
    def __init__(self):
        self.tz_dict = {
            "utc" : 0,
            "gmt" : 0,
            "est" : -5,
            "cst" : -6,
            "mst" : -7,
            "pst" : -8
        }

    async def parse_command(self, content, channel):

        # remove formatting
        content = content.replace(":", "")

        # run through string until we hit something not a number
        num_check = re.compile("[0-9]")

        index = 0
        while index < len(content):
            if not num_check.fullmatch(content[index]):
                break
            index += 1

        time_value = content[:index]
        if len(time_value) == 3:
            time_value = "0" + time_value
        elif len(time_value) < 3 or len(time_value) > 4:
            await channel.send("Your time formatting is heretical!  Proper servants of the emperor use three or four digits for times!")
            return

        content_no_spaces = content.replace(" ", "")

        # if there's an am or pm designation, update time accordingly
        time_code = content_no_spaces[index:index+2]
        if time_code.lower() == "am":
            content_no_spaces = content_no_spaces[index+2:]
        elif time_code.lower() == "pm":
            time_value = int(time_value) + 1200
            content_no_spaces = content_no_spaces[index+2:]
        
        await channel.send(time_value)
