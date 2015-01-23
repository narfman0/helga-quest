from helga.db import db
from helga.plugins import command, random_ack
from helga_quest.core import Being

import random

_help_text = 'Collaboratively play an RPG from user driven content \
Usage: !quest (mob|adventure|rest|attack|magic)'


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
        if enemy:
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
    elif args[0] == 'mob':
        being = Being(args[2])
        if args[1] == 'add':
            db.quest.enemies.insert(being)
        else:
            db.quest.enemies.remove(being)
    elif args[0] == "attack":
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
            return "Hit for %s, received %d damage" % dmg, received_dmg
    return ''
