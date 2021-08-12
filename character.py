from random import randrange as roll

class Character:
    def __init__(self, char_name, player_name):
        self.name = char_name
        self.player_name = player_name
        self.char_class = None
    
        self.char_stats = {
            "WS" : 0,
            "BS" : 0,
            "S" : 0,
            "T" : 0,
            "Agi" : 0,
            "Int" : 0,
            "Per" : 0,
            "Wil" : 0,
            "Fel" : 0
        }

        self.skills = []

        self.inventory = []

        self.xp_total = 5000
        self.xp_spent = 4500

    def generate_characteristics(self, mode=0):
        if mode == "random" or mode == 0:
            for stat in self.char_stats:
                die_roll = roll(1,11) + roll(1,11)
                self.char_stats[stat] = die_roll + 25
        else:
            for stat in self.char_stats:
                self.char_stats[stat] = 25
        return

    def print_stats(self):
        return self.char_stats