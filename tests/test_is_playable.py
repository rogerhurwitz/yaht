import unittest

from yaht.scorecard import Scorecard
from yaht.utils import Category, Combo
from yaht.validate import is_playable


class TestIsPlayable(unittest.TestCase):
    def setUp(self):
        self.card = Scorecard()

    # --- Upper Section Tests ---
    def test_upper_category_playable_with_matches(self):
        self.assertTrue(is_playable(Category.FOURS, Combo([4, 4, 2, 3, 6]), self.card))

    def test_upper_category_unplayable_with_no_matches(self):
        self.assertIs(is_playable(Category.SIXES, Combo([1, 2, 3, 4, 5]), self.card), False)

    def test_upper_category_unplayable_if_already_scored(self):
        self.card.set_category_score(Category.THREES, [3, 3, 3, 2, 1])
        self.assertIs(is_playable(Category.THREES, Combo([3, 3, 3, 2, 1]), self.card), False)

    # --- Lower Section: Three/Four of a Kind ---
    def test_three_of_a_kind_valid(self):
        self.assertTrue(
            is_playable(Category.THREE_OF_A_KIND, Combo([2, 2, 2, 4, 5]), self.card)
        )

    def test_four_of_a_kind_valid(self):
        self.assertTrue(
            is_playable(Category.FOUR_OF_A_KIND, Combo([5, 5, 5, 5, 2]), self.card)
        )

    def test_three_of_a_kind_invalid(self):
        self.assertIs(
            is_playable(Category.THREE_OF_A_KIND, Combo([2, 2, 3, 4, 5]), self.card), False
        )

    def test_four_of_a_kind_invalid(self):
        self.assertIs(
            is_playable(Category.FOUR_OF_A_KIND, Combo([5, 5, 5, 2, 2]), self.card), False
        )

    # --- Lower Section: Full House ---
    def test_full_house_valid(self):
        self.assertTrue(is_playable(Category.FULL_HOUSE, Combo([3, 3, 3, 6, 6]), self.card))

    def test_full_house_invalid(self):
        self.assertIs(
            is_playable(Category.FULL_HOUSE, Combo([3, 3, 4, 4, 6]), self.card), False
        )

    # --- Lower Section: Straights ---
    def test_small_straight_valid(self):
        self.assertTrue(
            is_playable(Category.SMALL_STRAIGHT, Combo([1, 2, 3, 4, 6]), self.card)
        )

    def test_small_straight_invalid(self):
        self.assertIs(
            is_playable(Category.SMALL_STRAIGHT, Combo([1, 1, 3, 4, 6]), self.card), False
        )

    def test_large_straight_valid(self):
        self.assertTrue(
            is_playable(Category.LARGE_STRAIGHT, Combo([2, 3, 4, 5, 6]), self.card)
        )

    def test_large_straight_invalid(self):
        self.assertIs(
            is_playable(Category.LARGE_STRAIGHT, Combo([1, 2, 2, 4, 5]), self.card), False
        )

    # --- YAHTZEE ---
    def test_yahtzee_valid(self):
        self.assertTrue(is_playable(Category.YAHTZEE, Combo([6, 6, 6, 6, 6]), self.card))

    def test_yahtzee_invalid(self):
        self.assertIs(is_playable(Category.YAHTZEE, Combo([6, 6, 6, 6, 5]), self.card), False)

    # --- CHANCE ---
    def test_chance_unscored_always_playable(self):
        self.assertTrue(is_playable(Category.CHANCE, Combo([1, 2, 3, 4, 5]), self.card))

    def test_chance_scored_unplayable(self):
        self.card.set_category_score(Category.CHANCE, [1, 2, 3, 4, 5])
        self.assertIs(is_playable(Category.CHANCE, Combo([1, 2, 3, 4, 5]), self.card), False)

    # --- Joker Rule Cases ---
    def test_joker_requires_upper_category(self):
        self.card.set_category_score(Category.YAHTZEE, [3, 3, 3, 3, 3])
        combo = Combo([3, 3, 3, 3, 3])
        self.assertTrue(is_playable(Category.THREES, combo, self.card))
        self.assertIs(is_playable(Category.FULL_HOUSE, combo, self.card), False)

    def test_joker_allows_lower_when_upper_scored(self):
        self.card.set_category_score(Category.YAHTZEE, [4, 4, 4, 4, 4])
        self.card.set_category_score(Category.FOURS, [4, 4, 4, 4, 4])
        combo = Combo([4, 4, 4, 4, 4])
        self.assertTrue(is_playable(Category.FULL_HOUSE, combo, self.card))

    def test_joker_denied_if_all_lower_scored(self):
        self.card.set_category_score(Category.YAHTZEE, [2] * 5)
        self.card.set_category_score(Category.TWOS, [2] * 5)
        for cat in Category:
            if cat not in {Category.YAHTZEE, Category.TWOS}:
                self.card.set_category_score(cat, [1, 2, 3, 4, 5])
        combo = Combo([2] * 5)
        self.assertIs(is_playable(Category.THREE_OF_A_KIND, combo, self.card), False)


if __name__ == "__main__":
    unittest.main()
