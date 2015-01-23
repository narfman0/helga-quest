from helga_quest.core import Being
from helga.db import db

VERSION = (1, 0, 0)

__version__ = '.'.join([str(v) for v in VERSION])

if not db.quest.hero:
    db.quest.hero = Being()
