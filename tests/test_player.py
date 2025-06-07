import unittest

from yaht.category import Category
from yaht.dice import Dice
from yaht.playable import is_playable
from yaht.player import TestPlayer
from yaht.scorecard import Scorecard


class TestTestPlayer(unittest.TestCase):
    def setUp(self):
        self.plyr = TestPlayer()
        self.card = Scorecard()
        self.dice = Dice()

    def test_instance(self):
        self.assertIsNotNone(self.plyr)

    def test_returns_category(self):
        category = self.plyr.take_turn(self.dice, self.card.view)
        self.assertIsInstance(category, Category)

    def test_fills_scorecard(self):
        for _ in range(13):
            category = self.plyr.take_turn(self.dice, self.card.view)

            self.assertTrue(
                is_playable(category, self.dice.values, self.card, True),
                f"{category} is not playable/unscored.",
            )
            self.card.zero_category(category)


if __name__ == "__main__":
    unittest.main()
