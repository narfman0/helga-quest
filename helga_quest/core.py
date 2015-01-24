""" Core classes to define rpg """
import math, jaraco.modb as encoder, random

class Being(object):
    """ Something that lives and breathes and can die """
    def __init__(self, name='Hero', hp=1, mana=1, attack=1, defense=1,
                 magic=1, mr=1, level=1, xp=0):
        self.hp = hp
        self.mana = mana
        self.attack = attack
        self.defense = defense
        self.magic = magic
        self.mr = mr
        self.name = name
        self.level = level
        self.xp = xp
        self.hp_current = self.hp
        self.mana_current = self.mana

    def do_attack(self, target):
        """ Weapon attack, returns dmg to be received. """
        return round(self.attack * (100. / (100. + target.defense)), 1)

    def do_magic(self, target):
        """ Magic attack, returns dmg to be received. """
        if self.mana > 0:
            power = random.randint(50, 100)
            self.mana -= (power / 10)
            return self.magic * ((100. + power) / (100. + target.mr))

    def killed(self, target):
        """ Handle killing something, first get xp then check level """
        self.xp += target.xp
        self.do_level()

    def do_level(self):
        """ Check if being should level up, do it if so """
        while self.xp > Being.xp_to_level(self.level + 1):
            self.level += 1
            self.hp += random.randint(5, 10)
            self.mana += random.randint(5, 10)
            self.attack += random.randint(0, 3)
            self.defense += random.randint(0, 3)
            self.magic += random.randint(0, 3)
            self.mr += random.randint(0, 3)
            self.hp_current = self.hp
            self.mana_current = self.mana

    def __unicode__(self):
        return '{} HP: {}/{} Level: {}'.format(self.name, self.hp_current, self.hp, self.level)

    def __repr__(self):
        return self.__unicode__()

    def encode(self):
        return encoder.encode(self)

    @staticmethod
    def decode(target):
        return encoder.decode(target)

    @staticmethod
    def xp_to_level(level):
        """ Calculate the amount of xp to get to the next level """
        if level <= 11:
            xp = 40 * math.pow(level, 2) + 360 * level
        elif level <= 27:
            xp = -.4 * math.pow(level, 3) + 40.4 * math.pow(level, 2) + 396 * level
        else:
            xp = (65 * math.pow(level, 2) - 165 * level - 6750) * .82
        return xp
