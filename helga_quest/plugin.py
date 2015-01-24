from helga.db import db
from helga.plugins import command, random_ack
from helga_quest.core import Being
from random import random

import json, math

_help_text = """Collaboratively play an RPG from user driven content \
Usage: !quest (mob|adventure|rest|attack|magic)\
!quest mob add '{"name":"Johnnie Tsunami", "hp":2, "level":2}'"""


def create_random_enemy():
    """ Grab random enemy from enemies collection """
    index = int(math.floor(random()*db.quest.enemies.count()))
    re = db.quest.enemies.find().limit(1).skip(index).next()
    return Being.decode(re)


@command('quest', help=_help_text, shlex=True)
def quest(client, channel, nick, message, cmd, args):
    """ Execute primary quest commands """
    hero = Being.decode(db.quest.heroes.find_one())
    enemy = None
    in_encounter = db.quest.encounter.count() > 0
    if in_encounter:
        enemy = Being.decode(db.quest.encounter.find_one())
    response = ''
    if len(args) == 0:
        response = str(hero)
        if not in_encounter:
            response += u", you are not actively fighting."
        else:
            response += ' vs %s.' % str(enemy)
        response += ' There are %d entries in the monster database' % db.quest.enemies.count()
    elif args[0] == 'adventure':
        if hero.hp_current <= 0:
            response = 'You must rest before adventuring!'
        elif in_encounter:
            response = "You can't abandon your valiant journey!"
        elif db.quest.enemies.count() == 0:
            response = "There are no enemies populated against which to quest!"
        else:
            enemy = create_random_enemy()
            db.quest.encounter.insert(enemy.encode())
            response = "You've encountered a {}!".format(enemy.name)
    elif args[0] == 'rest':
        if in_encounter:
            response = "You can't rest whilst in combat!"
        else:
            hero.hp_current = hero.hp
            response = 'You feel refreshed and ready for combat'
    elif args[0] == 'mob':
        stats = json.loads(args[2])
        being = Being(**stats)
        if args[1] == 'add':
            db.quest.enemies.insert(being.encode())
        elif args[1] == 'remove':
            db.quest.enemies.remove(being.encode())
    elif args[0] == "attack":
        if hero.hp_current <= 0:
            response = 'You must rest before exerting oneself!'
        if not in_encounter:
            response = "There is no enemy to attack!"
        dmg = hero.do_attack(enemy)
        enemy.hp_current -= dmg
        if enemy.hp_current <= 0:
            hero.killed(enemy)
            db.quest.encounter.remove(enemy.encode())
            response = "You've slain the {} and earned {} xp!".format(enemy.name, enemy.xp)
        else:
            received_dmg = enemy.do_attack(enemy)
            hero.hp_current -= received_dmg
            db.quest.heroes.update({'name':hero.name}, hero.encode())
            if hero.hp_current <= 0:
                db.quest.encounter.drop()
                response = 'You have been slain!'
            else:
                db.quest.encounter.update({'name':enemy.name}, enemy.encode())
                response = "Hit for {}, received {} damage".format(dmg, received_dmg)
    elif args[0] == "drop":
        if len(args) > 1:
            if args[1] == 'heroes':
                db.quest.heroes.drop()
                response = "Heroes dropped"
            elif args[1] == 'encounter':
                db.quest.encounter.drop()
                response = "Encounter dropped"
            elif args[1] == "enemies":
                db.quest.enemies.drop()
                response = "Enemies dropped"
            else:
                response = "I don't understand %s" % args[1]
        else:
            db.quest.drop()
            response = "Quest database dropped, so sad"
    else:
        response = "I don't understand %s" % args[0]
    return response
