""" Core classes to define rpg """
import math, random, re

class Action(object):
    """ A special attack a Being may execute against another Being """
    def __init__(self, name='Hero', description='{target} took {dmg} damage.',
                 hp=0, attack=0, defense=0, speed=0):
        self.name = name
        self.description = description
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.speed = speed

    def create_response(self, target, dmg):
        """ Create the string response the action should produce against the
        enemy. e.g. if the enemy's name is Phil, and his attack is Anthropy,
        the description might be
        'Phil's anthropy attack strikes to {target}'s heart, causing {dmg}
        damage'
        """
        result = self.description
        kwargs = {}
        if re.search('{\s*dmg\s*}', result, re.I):
            kwargs['dmg']=dmg
        if re.search('{\s*target\s*}', result, re.I):
            kwargs['target']=target.name
        if re.search('{\s*name\s*}', result, re.I):
            kwargs['name']=self.name
        return result.format(**kwargs)

    def __unicode__(self):
        """ Unicode representation of action """
        return 'Action for {}, description: {}'.format(self.name, self.description)

    def __repr__(self):
        """ String representation of action """
        return self.__unicode__()


class Being(object):
    """ Something that lives and breathes and can die """
    def __init__(self, name='Hero', hp=1, attack=1, defense=1, speed=50,
                 level=1, xp=0):
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.name = name
        self.level = level
        self.xp = xp
        self.hp_current = self.hp

    def do_attack(self, target, attack_bonus=0, defense_bonus=0):
        """ Weapon attack, returns dmg to be received. """
        return round((self.attack + attack_bonus) *
                     (100. / (100. + target.defense + defense_bonus)), 1)

    def killed(self, target):
        """ Handle killing something, first get xp then check level """
        self.xp += target.xp
        self.do_level()

    def do_level(self):
        """ Check if being should level up, do it if so """
        while self.xp > Being.xp_to_level(self.level + 1):
            self.level += 1
            self.hp += random.randint(5, 10)
            self.attack += random.randint(0, 3)
            self.defense += random.randint(0, 3)
            self.hp_current = self.hp

    def initiative_roll(self, target_speed):
        """ Roll for initiative per round, returns true if won """
        self_roll = self.speed + random.gauss(50, 16)
        target_roll = target_speed + random.gauss(50, 16)
        return self_roll > target_roll

    def __unicode__(self):
        """ String representation of being """
        return '{} HP: {}/{} Level: {}'.format(self.name, self.hp_current, self.hp, self.level)

    def __repr__(self):
        """ String representation of being """
        return self.__unicode__()

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
