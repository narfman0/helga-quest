from helga.db import db
from helga.plugins import command, random_ack
from helga_quest.core import Being

import json, random

_help_text = 'Collaboratively play an RPG from user driven content \
Usage: !quest (mob|adventure|rest|attack|magic)\
!quest mob add '{"name":"Johnnie Tsunami", "hp":2, "level":2}''


@command('quest', help=_help_text, shlex=True)
def quest(client, channel, nick, message, cmd, args):
    """ Execute primary quest commands """
    hero = db.quest.hero
    enemy = db.quest.enemy
    if len(args) == 0:
        status = str(hero)
        if not enemy:
            status += u", you are not actively fighting"
        else:
            status += ' vs %s' % str(enemy)
    if args[0] == 'adventure':
        if hero.hp_current <= 0:
            return 'You must rest before adventuring!'
        elif enemy:
            return "You can't abandon your valiant journey!"
        elif db.quest.enemies.count() == 0:
            return "There are no enemies populated against which to quest!"
        else:
            enemy = random.choice(db.quest.enemies)
            return "You've encountered a %s!" % enemy.name
    elif args[0] == 'rest':
        if enemy:
            return "You can't rest whilst in combat!"
        else:
            hero.hp_current = hero.hp
            return 'You feel refreshed and ready for combat'
    elif args[0] == 'mob':
        stats = json.loads(args[2])
        being = Being(**stats)
        if args[1] == 'add':
            db.quest.enemies.insert(being)
        elif args[1] == 'remove':
            db.quest.enemies.remove(being)
    elif args[0] == "attack":
        if hero.hp_current <= 0:
            return 'You must rest before exerting oneself!'
        if not enemy:
            return "There is no enemy to attack!"
        dmg = hero.do_attack(enemy)
        enemy.hp_current -= dmg
        if enemy.hp_current <= 0:
            hero.killed(enemy)
            db.quest.enemy = None
            return "You've slain the %s and earned %d xp!" % enemy.name, enemy.xp
        else:
            received_dmg = enemy.do_attack(enemy)
            hero.hp_current -= received_dmg
            if hero.hp_current <= 0:
                db.quest.enemy = None
                return 'You have been slain!'
            return "Hit for %s, received %d damage" % dmg, received_dmg
    return ''
