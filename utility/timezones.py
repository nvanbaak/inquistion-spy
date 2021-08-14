from datetime import time
import re
import discord


class Time_Manager:
    def __init__(self):
        self.tz_dict = {
            "utc" : 0,
            "gmt" : 0,
            "ist" : 5.5,
            "cest" : 2,
            "eet" : 2,
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

        # remove extra spaces
        while "  " in content:
            content = content.replace("  ", " ")

        # check if the seperator is ":"" or "h"
        separator = ""
        if ":" in content:
            separator = ":"
            content = content.replace(":", "").lower()
        if "h" in content.split(" ", 1)[0]:
            separator = "h"
            content = content.replace("h", "", 1).lower()
        else:
            content = content.lower()

        # run through string until we hit something not a number
        num_check = re.compile("[0-9]")

        index = 0
        while index < len(content):
            if not num_check.fullmatch(content[index]):
                break
            index += 1

        time_value = content[:index]
        if len(time_value) == 1:
            time_value = "0{}00".format(time_value)
        elif len(time_value) == 2:
            time_value = "{}00".format(time_value)
        elif len(time_value) == 3:
            time_value = "0{}".format(time_value)
        elif len(time_value) > 4:
            await channel.send("Your time formatting is heretical!  No Emperor-fearing citizen needs more than four numbers for keeping track of time!")
            raise TypeError("Incorrect value for time command")

        content = time_value + content[index:]

        # remove spaces between any am/pm designations and their times
        content = content.replace(" pm ", "p ")
        content = content.replace("pm ", "p ")
        content = content.replace(" p ", "p ")
        content = content.replace(" am ", "a ")
        content = content.replace("am ", "a ")
        content = content.replace(" a ", "a ")

        # if am/pm exists, it's now the next character after the time code. If pm, convert to 24-hour time:
        hour_format = 24
        if content[4] == "p":
            time_value = str(int(time_value) + 1200)
            hour_format = 12
            separator = ":"
        elif content[4] == "a":
            hour_format = 12
            separator = ":"

        # original timezone is the first argument, destination is the rest
        origin = content.split(" ")[1]
        dest = content.split(" ")[2:]

        formatted_time = self.format_timecode(time_value, hour_format, separator)

        output_str = "{} {} is: \n - ".format(formatted_time, origin.upper())

        # if there's just one destination, we make it one line and delete the colon
        if len(dest) == 1:
            output_str = output_str[:-6] + " "

        for tz in dest:
            try:
                converted_time = self.translate_timezones(time_value, origin, tz)

                new_time = self.format_timecode(converted_time, hour_format, separator)

                output_str += "{} {} \n - ".format(new_time, tz.upper())

            except KeyError:
                await channel.send("Heresy!  I don't recognize the time zone \"{}\".  Please report this oversight to the Administratum.".format(tz))
                return

        # when we're done, there's a hanging bullet point, so let's clean that up
        output_str = output_str[:-5]

        await channel.send(output_str)

    def translate_timezones(self, time_value, origin, dest):

        in_utc = self.utc(time_value, origin)
        converted_time = self.un_utc(in_utc, dest)

        return converted_time

    def utc(self, time_code, tz_code):
        if tz_code == "utc" or tz_code == "gmt":
            return time_code

        hours = int(time_code[:2])
        yesterday = False
        tomorrow = False

        time_diff = self.tz_dict[tz_code]

        # check for half-hour differences
        if not isinstance(time_diff, int):
            # round up to an hour
            time_diff = int(time_diff + 0.5)
            
            # add half an hour to the time code
            minutes = int(time_code[2:4])
            minutes += 30

            # if that's too many minues, reset and decrease the time diff to compensate
            if minutes >= 60:
                minutes -= 60
                time_diff -= 1
                if minutes < 10:
                    minutes = "0" + str(minutes)

            # insert updated minutes
            time_code = time_code[0:2] + str(minutes) + time_code[4:]

        in_utc = hours - time_diff

        # check rollover
        if in_utc < 0:
            in_utc += 24
            yesterday = True

        if in_utc >= 24:
            in_utc -= 24
            tomorrow = True

        if in_utc < 10:
            in_utc = "0" + str(in_utc)

        new_time = str(in_utc) + time_code[2:]

        if tomorrow:
            new_time += "T"
        if yesterday:
            new_time += "Y"

        return new_time

    def un_utc(self, time_code, tz_code):
        if tz_code == "utc" or tz_code == "gmt":
            return time_code

        hours = int(time_code[:2])
        yesterday = False
        tomorrow = False

        # check if the utc function left a day flag; if so, delete it and update the booleans
        if time_code[-1] == "T":
            tomorrow = True
            time_code = time_code[:-1]

        if time_code[-1] == "Y":
            yesterday = True
            time_code = time_code[:-1]

        time_diff = self.tz_dict[tz_code]

        # check for half-hour differences
        if not isinstance(time_diff, int):
            # round down to an hour
            time_diff = int(time_diff - 0.5)
            
            # add half an hour to the time code
            minutes = int(time_code[2:4])
            minutes += 30

            # if that's too many minues, reset and increase the time diff to compensate
            if minutes >= 60:
                minutes -= 60
                time_diff += 1

                if minutes < 10:
                    minutes = "0" + str(minutes)

            # insert updated minutes
            time_code = time_code[0:2] + str(minutes) + time_code[4:]

        not_utc = hours + time_diff

        if not_utc < 0:
            not_utc += 24
            if tomorrow:
                tomorrow = False
            else:
                yesterday = True

        if not_utc >= 24:
            not_utc -= 24
            if yesterday:
                yesterday = False
            else:
                tomorrow = True

        if not_utc < 10:
            not_utc = "0" + str(not_utc)

        new_time = str(not_utc) + time_code[2:]

        if tomorrow:
            new_time += "T"
        if yesterday:
            new_time += "Y"

        return new_time

    def format_timecode(self, time_code, hour_format, sep_format):

        if len(time_code) == 3:
            time_code = "0" + time_code

        # parse and remove day rollover flags
        tomorrow = time_code[-1] == "T"
        yesterday = time_code[-1] == "Y"

        if tomorrow or yesterday:
            time_code = time_code[:-1]

        # if we're using 12-hour time, convert and add am/pm
        if hour_format == 12:
            hours = int(time_code[:2])
            if hours > 12:
                hours -= 12
                time_code = str(hours) + time_code[2:] + " pm"
            elif hours == 12:
                time_code = "12" + time_code[2:] + " pm"
            elif hours == 0:
                time_code = "12" + time_code[2:] + " am"
            else:
                time_code = str(hours) + time_code[2:] + " am"

        # insert separator after the hour digits
        if not sep_format == "":
            time_code = time_code[:2] + sep_format + time_code[2:]

            # then delete leading 0 if one exists
            if time_code[0] == "0":
                time_code = time_code[1:]

        # add rollover notification
        if tomorrow:
            time_code += " (next day)"
        if yesterday:
            time_code += " (previous day)"

        return time_code