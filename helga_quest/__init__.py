from helga.db import db
from helga_quest.core import Being
from helga_quest.util import encode

VERSION = (1, 0, 0)

__version__ = '.'.join([str(v) for v in VERSION])

if db.quest.heroes.count() == 0:
    db.quest.heroes.insert(encode(Being()))
