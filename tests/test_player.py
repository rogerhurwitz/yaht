import unittest

from yaht.category import Category
from yaht.dice import Dice
from yaht.exceptions import InvalidCategoryError
from yaht.playable import is_playable
from yaht.player import TestPlayer
from yaht.scorecard import Scorecard


class TestTestPlayer(unittest.TestCase):
    def setUp(self):
        self.plyr = TestPlayer()
        self.card = Scorecard()

    def _play_full_game(self):
        for _turn in range(13):
            dice = Dice()
            category = self.plyr.take_turn(dice, self.card.view)
            if not is_playable(category, dice.values, self.card, match_zero_playable=True):
                raise InvalidCategoryError(f"Category: {category}")

            if is_playable(category, dice.values, self.card, match_zero_playable=False):
                self.card.set_category_score(category, dice.values)
            else:
                self.card.zero_category(category, dice.values)

    def test_player_not_none(self):
        self.assertIsNotNone(self.plyr)

    def test_player_returns_category(self):
        dice = Dice()
        category = self.plyr.take_turn(dice, self.card.view)
        self.assertIsInstance(category, Category)

    def test_player_completes_game(self):
        self._play_full_game()

    @unittest.skip("Subject test under review.")
    def test_player_scores_above_200(self):
        self._play_full_game()
        self.assertGreater(self.card.get_card_score(), 200)


if __name__ == "__main__":
    unittest.main()
