from helga.db import db
from helga.plugins import command, random_ack
from helga_quest.core import Action, Being
from random import random

import jaraco.modb, json, math

_help_text = """Collaboratively play an RPG from user driven content \
Usage: !quest (action|adventure|attack|mob|rest)\
!quest mob add '{"name":"Assault Shaker", "hp":1, "level":1, "xp":60}'\
!quest action add '{"name":"Assault Shaker", "description":"{name} peppers {target} for {dmg} damage", "attack":5}'\
!quest adventure\
helga> You've encountered a Assault Shaker!\
!quest attack\
helga> You strike for 1 damage, Assault Shaker peppers Hero for 5.9 damage"""


def encode(target):
    """ Encode as mongodb friendly object """
    return jaraco.modb.encode(target)

def decode(target):
    """ Decode from mongodb """
    return jaraco.modb.decode(target)

def random_cursor(cursor):
    """ Pull a random item from a cursor """
    index = int(math.floor(random()*cursor.count()))
    return cursor.limit(1).skip(index).next()

@command('quest', help=_help_text, shlex=True)
def quest(client, channel, nick, message, cmd, args):
    """ Execute primary quest commands """
    hero = decode(db.quest.heroes.find_one())
    enemy = None
    in_encounter = db.quest.encounter.count() > 0
    if in_encounter:
        enemy = decode(db.quest.encounter.find_one())
    response = ''
    if len(args) == 0:
        response = str(hero)
        if not in_encounter:
            response += u", you are not actively fighting."
        else:
            response += ' vs %s.' % str(enemy)
        response += ' There are {} mobs and {} actions in database'.format(db.quest.enemies.count(), db.quest.actions.count())
    elif args[0] == 'action' or args[0] == 'actions':
        stats = json.loads(args[2])
        action = Action(**stats)
        if args[1] == 'add':
            db.quest.actions.insert(encode(action))
        elif args[1] == 'remove':
            db.quest.actions.remove({'name':action.name, 'description':action.description})
        else:
            response = 'I do not understand %s' % args[2]
    elif args[0] == 'adventure':
        if hero.hp_current <= 0:
            response = 'You must rest before adventuring!'
        elif in_encounter:
            response = "You can't abandon your valiant journey!"
        elif db.quest.enemies.count() == 0:
            response = "There are no enemies populated against which to quest!"
        else:
            if len(args) > 1:
                query = db.quest.enemies.find({'name':args[1]})
            else:
                query = db.quest.enemies.find()
            enemy = decode(random_cursor(query))
            db.quest.encounter.insert(encode(enemy))
            response = "You've encountered a {}!".format(enemy.name)
    elif args[0] == 'rest':
        if in_encounter:
            response = "You can't rest whilst in combat!"
        else:
            hero.hp_current = hero.hp
            db.quest.heroes.remove({'name':hero.name})
            db.quest.heroes.insert(encode(hero))
            response = 'You feel refreshed and ready for combat'
    elif args[0] == 'mob' or args[0] == 'mobs':
        stats = json.loads(args[2])
        being = Being(**stats)
        if args[1] == 'add':
            db.quest.enemies.insert(encode(being))
        elif args[1] == 'remove':
            db.quest.enemies.remove({'name':being.name})
    elif args[0] == "attack":
        if hero.hp_current <= 0:
            response = 'You must rest before exerting oneself!'
        elif not in_encounter:
            response = "There is no enemy to attack!"
        else:
            # grab enemy action to have defense bonus on hand
            action = None
            query = db.quest.actions.find({'name':enemy.name})
            if query.count() > 0:
                action = decode(random_cursor(query))
            defense_bonus = action.defense if action else 0
            dmg = hero.do_attack(enemy, defense_bonus=defense_bonus)
            enemy.hp_current -= dmg
            response = 'You strike for %d damage, ' % dmg
            if enemy.hp_current <= 0:
                hero.killed(enemy)
                db.quest.heroes.remove({'name':hero.name})
                db.quest.heroes.insert(encode(hero))
                db.quest.encounter.remove({'name':enemy.name})
                response += "you've slain the {}, and earned {} xp!".format(enemy.name, enemy.xp)
            else:
                attack_bonus = action.attack if action else 0
                received_dmg = enemy.do_attack(hero, attack_bonus=attack_bonus)
                hero.hp_current -= received_dmg
                db.quest.heroes.remove({'name':hero.name})
                db.quest.heroes.insert(encode(hero))
                if action:
                    response += action.create_response(hero, received_dmg)
                else:
                    response += "and received {} damage.".format(dmg, received_dmg)
                if hero.hp_current <= 0:
                    db.quest.encounter.drop()
                    response += '\nYou have been slain!'
                else:
                    db.quest.encounter.remove({'name':enemy.name})
                    db.quest.encounter.insert(encode(enemy))
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
