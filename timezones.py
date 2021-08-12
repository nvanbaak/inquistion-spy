import re
import discord


class Time_Manager:
    def __init__(self):
        self.tz_dict = {
            "utc" : 0,
            "gmt" : 0,
            "edt" : -4,
            "est" : -5,
            "cdt" : -5,
            "cst" : -6,
            "mdt" : -6,
            "mst" : -7,
            "pdt" : -7,
            "pst" : -8
        }

    async def parse_command(self, content, channel):

        # remove colons and extra spaces
        content = content.replace(":", "").lower()
        while "  " in content:
            content = content.replace("  ", " ")

        # run through string until we hit something not a number
        num_check = re.compile("[0-9]")

        index = 0
        while index < len(content):
            if not num_check.fullmatch(content[index]):
                break
            index += 1

        # check that time code is the proper length
        time_value = content[:index]
        if len(time_value) == 3:
            time_value = "0" + time_value
        elif len(time_value) < 3 or len(time_value) > 4:
            await channel.send("Your time formatting is heretical!  Proper servants of the emperor use three or four digits for times!")
            raise TypeError("Incorrect value for time command")

        # remove spaces between any am/pm designations and their times
        content = content.replace(" pm ", "pm ")
        content = content.replace(" am ", "am ")

        # if am/pm exists, it's now the next two characters after the time code. If pm, convert to 24-hour time:
        if content[index:index+2] == "pm":
            time_value = str(int(time_value) + 1200)

        # original timezone is the first argument, destination is the second
        origin = content.split(" ")[1]
        dest = content.split(" ")[2]

        converted_time = self.translate_timezones(time_value, origin, dest)

        time_value = self.format_timecode(time_value)
        new_time = self.format_timecode(converted_time)

        output = "{} {} is **{} {}**".format(time_value, origin.upper(), new_time, dest.upper())

        await channel.send(output)

    def translate_timezones(self, time_value, origin, dest):

        in_utc = self.utc(time_value, origin)
        converted_time = self.un_utc(in_utc, dest)

        return converted_time

    def utc(self, time_code, tz_code):
        if time_code == "utc" or time_code == "gmt":
            return time_code

        hours = time_code[:2]
        yesterday = False
        tomorrow = False

        in_utc = int(hours) - self.tz_dict[tz_code]

        if in_utc < 0:
            in_utc += 24
            yesterday = True

        if in_utc >= 24:
            in_utc -= 24
            tomorrow = True

        new_time = str(in_utc) + time_code[2:]

        return new_time

    def un_utc(self, time_code, tz_code):
        if time_code == "utc" or time_code == "gmt":
            return time_code

        hours = time_code[:2]
        yesterday = False
        tomorrow = False

        not_utc = int(hours) + self.tz_dict[tz_code]

        if not_utc < 0:
            not_utc += 24
            yesterday = True

        if not_utc >= 24:
            not_utc -= 24
            tomorrow = True

        new_time = str(not_utc) + time_code[2:]

        return new_time

    def format_timecode(self, time_code):

        if len(time_code) == 3:
            time_code = "0" + time_code

        # add colon
        time_code = time_code[:2] + ":" + time_code[2:]

        # convert 24 to 12
        hours = int(time_code[:2])
        if hours > 12:
            hours -= 12
        time_code = str(hours) + time_code[2:] + " pm"

        return time_code