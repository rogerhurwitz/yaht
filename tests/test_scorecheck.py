import unittest

from yaht.category import Category
from yaht.dicetypes import DiceRoll
from yaht.scorecard import Scorecard
from yaht.scorecheck import is_combo_scoreable


class TestIsPlayable(unittest.TestCase):
    def setUp(self):
        self.card = Scorecard()

    # --- Upper Section Tests ---
    def test_upper_category_playable_with_matches(self):
        self.assertTrue(
            is_combo_scoreable(Category.FOURS, DiceRoll([4, 4, 2, 3, 6]), self.card)
        )

    def test_upper_category_playable_with_no_matches(self):
        self.assertIs(
            is_combo_scoreable(Category.SIXES, DiceRoll([1, 2, 3, 4, 5]), self.card), True
        )

    def test_upper_category_unplayable_if_already_scored(self):
        self.card.set_category_score(Category.THREES, DiceRoll([3, 3, 3, 2, 1]))
        self.assertIs(
            is_combo_scoreable(Category.THREES, DiceRoll([3, 3, 3, 2, 1]), self.card), False
        )

    # --- Lower Section: Three/Four of a Kind ---
    def test_three_of_a_kind_valid(self):
        self.assertTrue(
            is_combo_scoreable(Category.THREE_OF_A_KIND, DiceRoll([2, 2, 2, 4, 5]), self.card)
        )

    def test_four_of_a_kind_valid(self):
        self.assertTrue(
            is_combo_scoreable(Category.FOUR_OF_A_KIND, DiceRoll([5, 5, 5, 5, 5]), self.card)
        )

    def test_three_of_a_kind_invalid(self):
        self.assertIs(
            is_combo_scoreable(Category.THREE_OF_A_KIND, DiceRoll([2, 2, 3, 4, 5]), self.card),
            False,
        )

    def test_four_of_a_kind_invalid(self):
        self.assertIs(
            is_combo_scoreable(Category.FOUR_OF_A_KIND, DiceRoll([5, 5, 5, 2, 2]), self.card),
            False,
        )

    # --- Lower Section: Full House ---
    def test_full_house_valid(self):
        self.assertTrue(
            is_combo_scoreable(Category.FULL_HOUSE, DiceRoll([3, 3, 3, 6, 6]), self.card)
        )

    def test_full_house_invalid(self):
        self.assertIs(
            is_combo_scoreable(Category.FULL_HOUSE, DiceRoll([3, 3, 4, 4, 6]), self.card),
            False,
        )

    def test_full_house_yahtzee_valid_1(self):
        self.card.zero_category(Category.YAHTZEE, DiceRoll([1, 1, 1, 1, 1]))
        self.card.zero_category(Category.THREES, DiceRoll([3, 4, 5, 2, 1]))
        self.assertIs(
            is_combo_scoreable(Category.FULL_HOUSE, DiceRoll([3, 3, 3, 3, 3]), self.card), True
        )

    def test_full_house_yahtzee_valid_2(self):
        self.assertIs(
            is_combo_scoreable(Category.FULL_HOUSE, DiceRoll([3, 3, 3, 3, 3]), self.card), True
        )

    def test_full_house_yahtzee_invalid(self):
        self.card.zero_category(Category.YAHTZEE, DiceRoll([1, 1, 1, 1, 1]))
        self.assertIs(
            is_combo_scoreable(Category.FULL_HOUSE, DiceRoll([3, 3, 3, 3, 3]), self.card),
            False,
        )

    # --- Lower Section: Straights ---
    def test_small_straight_valid(self):
        self.assertTrue(
            is_combo_scoreable(Category.SMALL_STRAIGHT, DiceRoll([1, 2, 3, 4, 6]), self.card)
        )

    def test_small_straight_invalid(self):
        self.assertIs(
            is_combo_scoreable(Category.SMALL_STRAIGHT, DiceRoll([1, 1, 3, 4, 6]), self.card),
            False,
        )

    def test_large_straight_valid(self):
        self.assertTrue(
            is_combo_scoreable(Category.LARGE_STRAIGHT, DiceRoll([2, 3, 4, 5, 6]), self.card)
        )

    def test_large_straight_invalid(self):
        self.assertIs(
            is_combo_scoreable(Category.LARGE_STRAIGHT, DiceRoll([1, 2, 2, 4, 5]), self.card),
            False,
        )

    # --- YAHTZEE ---
    def test_yahtzee_valid(self):
        self.assertTrue(
            is_combo_scoreable(Category.YAHTZEE, DiceRoll([6, 6, 6, 6, 6]), self.card)
        )

    def test_yahtzee_invalid(self):
        self.assertIs(
            is_combo_scoreable(Category.YAHTZEE, DiceRoll([6, 6, 6, 6, 5]), self.card), False
        )

    # --- CHANCE ---
    def test_chance_unscored_always_playable(self):
        self.assertTrue(
            is_combo_scoreable(Category.CHANCE, DiceRoll([1, 2, 3, 4, 5]), self.card)
        )

    def test_chance_scored_unplayable(self):
        self.card.set_category_score(Category.CHANCE, DiceRoll([1, 2, 3, 4, 5]))
        self.assertIs(
            is_combo_scoreable(Category.CHANCE, DiceRoll([1, 2, 3, 4, 5]), self.card), False
        )

    # --- Joker Rule Cases ---
    def test_joker_requires_upper_category(self):
        self.card.set_category_score(Category.YAHTZEE, DiceRoll([3, 3, 3, 3, 3]))
        combo = DiceRoll([3, 3, 3, 3, 3])
        self.assertTrue(is_combo_scoreable(Category.THREES, combo, self.card))
        self.assertIs(is_combo_scoreable(Category.FULL_HOUSE, combo, self.card), False)

    def test_joker_allows_lower_when_upper_scored(self):
        self.card.set_category_score(Category.YAHTZEE, DiceRoll([4, 4, 4, 4, 4]))
        self.card.set_category_score(Category.FOURS, DiceRoll([4, 4, 4, 4, 4]))
        combo = DiceRoll([4, 4, 4, 4, 4])
        self.assertTrue(is_combo_scoreable(Category.FULL_HOUSE, combo, self.card))

    def test_joker_denied_if_all_scored(self):
        for cat in Category:
            self.card.zero_category(cat, DiceRoll([1, 1, 1, 1, 1]))
        combo = DiceRoll([2] * 5)
        self.assertIs(is_combo_scoreable(Category.THREE_OF_A_KIND, combo, self.card), False)


if __name__ == "__main__":
    unittest.main()
