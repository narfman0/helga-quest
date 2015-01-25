""" Driver for core gameplay """
from helga.db import db
from helga_quest.core import Action, Being
from random import random
from helga_quest.util import encode, decode, random_cursor, current_state
import json

def status():
    """ Return the current status of the game as string """
    hero, enemy, in_encounter = current_state()
    next_xp = Being.xp_to_level(hero.level + 1)
    response = '{} XP: {}/{}'.format(str(hero), hero.xp, next_xp)
    if not in_encounter:
        response += u", you are not actively fighting."
    else:
        response += ' vs %s.' % str(enemy)
    template = ' There are {} mobs and {} actions in database'
    response += template.format(db.quest.enemies.count(),
                                db.quest.actions.count())
    return response

def action(mod, statsstr):
    """ Add/remove actions for NPCs """
    stats = json.loads(statsstr)
    action = Action(**stats)
    if mod == 'add':
        db.quest.actions.insert(encode(action))
    elif mod == 'remove':
        db.quest.actions.remove({'name':action.name,
                                 'description':action.description})
    else:
        response = 'I do not understand %s' % mod
    return response

def adventure(mob=''):
    """ Begin new encounter """
    hero, enemy, in_encounter = current_state()
    if hero.hp_current <= 0:
        response = 'You must rest before adventuring!'
    elif in_encounter:
        response = "You can't abandon your valiant journey!"
    elif db.quest.enemies.count() == 0:
        response = "There are no enemies populated against which to quest!"
    else:
        if mob:
            query = db.quest.enemies.find({'name':mob})
        else:
            query = db.quest.enemies.find()
        enemy = decode(random_cursor(query))
        db.quest.encounter.insert(encode(enemy))
        response = "You've encountered a {}!".format(enemy.name)
    return response

def rest():
    """ Direct player to rest if possible """
    hero, enemy, in_encounter = current_state()
    if in_encounter:
        response = "You can't rest whilst in combat!"
    else:
        hero.hp_current = hero.hp
        db.quest.heroes.remove({'name':hero.name})
        db.quest.heroes.insert(encode(hero))
        response = 'You feel refreshed and ready for combat'
    return response

def mob(mod, statsstr):
    """ Manage mobs in database """
    stats = json.loads(statsstr)
    being = Being(**stats)
    if mod == 'add':
        db.quest.enemies.insert(encode(being))
    elif mod == 'remove':
        db.quest.enemies.remove({'name':being.name})
    return response

def attack():
    """ Execute attack on current encounter mob(s) """
    hero, enemy, in_encounter = current_state()
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
            template = "you've slain the {}, and earned {} xp!"
            response += template.format(enemy.name, enemy.xp)
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
    return response

def drop(mod=''):
    """ Drop items from database """
    if not mod:
        db.quest.drop()
        response = "Quest database dropped, so sad"
    elif mod == 'heroes':
        db.quest.heroes.drop()
        response = "Heroes dropped"
    elif mod == 'encounter':
        db.quest.encounter.drop()
        response = "Encounter dropped"
    elif mod == "enemies":
        db.quest.enemies.drop()
        response = "Enemies dropped"
    else:
        response = "I don't understand %s" % mod
    return response
