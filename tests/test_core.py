import unittest
from helga_quest import core

class TestResults(unittest.TestCase):
    def setUp(self):
        self.roger = core.Being('Roger')
        self.roger.attack = 5
        self.enemy = core.Being('Enemy')
        self.enemy.xp = 2000

    def test_combat(self):
        """ verify combat """
        dmg = self.roger.do_attack(self.enemy)
        self.enemy.hp_current -= dmg
        self.assertTrue(dmg > 4)

    def test_defense(self):
        highdef = core.Being('Defense')
        highdef.defense = 200
        dmg = self.roger.do_attack(highdef)
        self.assertTrue(dmg < 2)

    def test_level(self):
        leveler = core.Being('Pwrlvl')
        leveler.xp = 5000
        leveler.do_level()
        self.assertEquals(leveler.level, 7)


if __name__ == '__main__':
    unittest.main()
