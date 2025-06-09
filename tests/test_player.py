import unittest

from yaht.category import Category
from yaht.dice import Dice
from yaht.exceptions import InvalidCategoryError
from yaht.player import TestPlayer
from yaht.scorecard import Scorecard
from yaht.scorecheck import is_scoreable


class TestTestPlayer(unittest.TestCase):
    def setUp(self):
        self.plyr = TestPlayer()
        self.card = Scorecard()

    def _play_full_game(self):
        for _turn in range(13):
            dice = Dice()
            category = self.plyr.take_turn(dice, self.card.view)
            if not is_scoreable(category, dice.values, self.card, zero_scoring_okay=True):
                raise InvalidCategoryError(f"Category: {category}")

            if is_scoreable(category, dice.values, self.card, zero_scoring_okay=False):
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
