
import unittest
from yaht.scorecard import Scorecard, Category
from yaht.exceptions import (
    DiceCountError, DieValueError, CategoryAlreadyScored, InvalidCategoryError
)
from enum import Enum

class TestScorecardStandard(unittest.TestCase):
    def setUp(self):
        self.card = Scorecard()

    def test_scorecard_type(self):
        """Confirm that scorecard is an instance of Scorecard."""
        self.assertIsInstance(self.card, Scorecard)

    def test_initial_score(self):
        """Confirm that scorecard initial score total is zero."""
        self.assertEqual(self.card.get_score(), 0)

    def test_aces_scoring(self):
        self.card.set_category_score(Category.ACES, [1, 1, 2, 3, 4])
        self.assertEqual(self.card.get_category_score(Category.ACES), 2)

    def test_zero_score_when_no_dice_match(self):
        self.card.set_category_score(Category.TWOS, [1, 1, 3, 4, 5])
        self.assertEqual(self.card.get_category_score(Category.TWOS), 0)

    def test_category_already_scored(self):
        self.card.set_category_score(Category.THREES, [3, 3, 3, 2, 1])
        with self.assertRaises(CategoryAlreadyScored):
            self.card.set_category_score(Category.THREES, [3, 3, 3, 3, 3])

    def test_invalid_dice_count(self):
        with self.assertRaises(DiceCountError):
            self.card.set_category_score(Category.FOURS, [4, 4, 4])

    def test_invalid_die_value(self):
        with self.assertRaises(DieValueError):
            self.card.set_category_score(Category.FIVES, [5, 5, 5, 5, 7])

    def test_three_of_a_kind_valid(self):
        self.card.set_category_score(Category.THREE_OF_A_KIND, [2, 2, 2, 4, 5])
        self.assertEqual(self.card.get_category_score(Category.THREE_OF_A_KIND), 15)

    def test_full_house_scoring(self):
        self.card.set_category_score(Category.FULL_HOUSE, [3, 3, 3, 6, 6])
        self.assertEqual(self.card.get_category_score(Category.FULL_HOUSE), 25)

    def test_small_straight_valid(self):
        self.card.set_category_score(Category.SMALL_STRAIGHT, [1, 2, 3, 4, 6])
        self.assertEqual(self.card.get_category_score(Category.SMALL_STRAIGHT), 30)

    def test_large_straight_valid(self):
        self.card.set_category_score(Category.LARGE_STRAIGHT, [2, 3, 4, 5, 6])
        self.assertEqual(self.card.get_category_score(Category.LARGE_STRAIGHT), 40)

    def test_yahtzee_scoring(self):
        self.card.set_category_score(Category.YAHTZEE, [6, 6, 6, 6, 6])
        self.assertEqual(self.card.get_category_score(Category.YAHTZEE), 50)

    def test_chance_scoring(self):
        self.card.set_category_score(Category.CHANCE, [1, 2, 3, 4, 5])
        self.assertEqual(self.card.get_category_score(Category.CHANCE), 15)

    def test_invalid_category(self):
        with self.assertRaises(InvalidCategoryError):
            self.card.set_category_score("INVALID", [1, 2, 3, 4, 5])

    def test_null_dice_sets_zero(self):
        self.card.set_category_score(Category.FIVES, None)
        self.assertEqual(self.card.get_category_score(Category.FIVES), 0)

class TestScorecardBonuses(unittest.TestCase):
    def setUp(self):
        self.card = Scorecard()

    def test_upper_section_bonus_awarded(self):
        # Score exactly 63: three of each 1–6
        self.card.set_category_score(Category.ACES, [1, 1, 1, 2, 3])
        self.card.set_category_score(Category.TWOS, [2, 2, 2, 1, 3])
        self.card.set_category_score(Category.THREES, [3, 3, 3, 2, 1])
        self.card.set_category_score(Category.FOURS, [4, 4, 4, 1, 2])
        self.card.set_category_score(Category.FIVES, [5, 5, 5, 1, 2])
        self.card.set_category_score(Category.SIXES, [6, 6, 6, 1, 2])
        total = self.card.get_score()
        self.assertGreaterEqual(total, 63 + 35)

    def test_yahtzee_bonus_applied(self):
        # Score initial Yahtzee
        self.card.set_category_score(Category.YAHTZEE, [6, 6, 6, 6, 6])
        # Score additional Yahtzee (should trigger bonus)
        self.card.set_category_score(Category.SIXES, [6, 6, 6, 6, 6])
        # One bonus chip = +100
        total = self.card.get_score()
        self.assertGreaterEqual(total, 50 + 30 + 100)  # YAHTZEE + SIXES + bonus

class TestScorecardJokerRules(unittest.TestCase):
    def setUp(self):
        self.card = Scorecard()

    def test_joker_rule_used_when_yahtzee_zeroed(self):
        # First YAHTZEE is zeroed
        self.card.set_category_score(Category.YAHTZEE, None)
        # Later roll a Yahtzee again (e.g., five 4s)
        self.card.set_category_score(Category.FOURS, [4, 4, 4, 4, 4])
        self.assertEqual(self.card.get_category_score(Category.FOURS), 20)

    def test_joker_rule_applies_to_lower_section_if_upper_filled(self):
        # Zero YAHTZEE and fill FOURS
        self.card.set_category_score(Category.YAHTZEE, None)
        self.card.set_category_score(Category.FOURS, [4, 4, 2, 1, 1])  # FOURS = 8
        # Now roll five 4s again
        self.card.set_category_score(Category.FULL_HOUSE, [4, 4, 4, 4, 4])
        self.assertEqual(self.card.get_category_score(Category.FULL_HOUSE), 25)

    def test_joker_rule_fallback_zero(self):
        # Zero YAHTZEE and fill all legal options
        self.card.set_category_score(Category.YAHTZEE, None)
        self.card.set_category_score(Category.FOURS, [4, 4, 2, 1, 1])
        self.card.set_category_score(Category.FULL_HOUSE, [2, 2, 3, 3, 3])
        self.card.set_category_score(Category.THREE_OF_A_KIND, [2, 2, 2, 4, 5])
        self.card.set_category_score(Category.FOUR_OF_A_KIND, [6, 6, 6, 6, 3])
        self.card.set_category_score(Category.SMALL_STRAIGHT, [1, 2, 3, 4, 6])
        self.card.set_category_score(Category.LARGE_STRAIGHT, [2, 3, 4, 5, 6])
        self.card.set_category_score(Category.CHANCE, [1, 1, 1, 2, 3])
        # Now joker forced to fill a zero in an upper section box
        with self.assertRaises(CategoryAlreadyScored):
            self.card.set_category_score(Category.FOURS, [4, 4, 4, 4, 4])

class TestScorecardJokerRuleEnforcement(unittest.TestCase):
    def setUp(self):
        self.card = Scorecard()

    def test_reject_illegal_joker_category(self):
        # Zero out the YAHTZEE box
        self.card.set_category_score(Category.YAHTZEE, None)
        # Fill required Upper Section box (e.g., FOURS)
        self.card.set_category_score(Category.FOURS, [4, 4, 1, 2, 3])
        # Fill all Lower Section joker targets
        self.card.set_category_score(Category.FULL_HOUSE, [3, 3, 3, 2, 2])
        self.card.set_category_score(Category.THREE_OF_A_KIND, [2, 2, 2, 4, 5])
        self.card.set_category_score(Category.FOUR_OF_A_KIND, [6, 6, 6, 6, 1])
        self.card.set_category_score(Category.SMALL_STRAIGHT, [1, 2, 3, 4, 5])
        self.card.set_category_score(Category.LARGE_STRAIGHT, [2, 3, 4, 5, 6])
        self.card.set_category_score(Category.CHANCE, [1, 1, 3, 4, 6])
        # Try to place a Yahtzee of 4s into Full House again (should fail)
        with self.assertRaises(CategoryAlreadyScored):
            self.card.set_category_score(Category.FULL_HOUSE, [4, 4, 4, 4, 4])

    def test_allow_valid_joker_category_when_upper_box_taken(self):
        self.card.set_category_score(Category.YAHTZEE, None)
        self.card.set_category_score(Category.FIVES, [5, 5, 1, 2, 3])
        # YAHTZEE of 5s, valid Joker placement in Chance
        self.card.set_category_score(Category.CHANCE, [5, 5, 5, 5, 5])
        self.assertEqual(self.card.get_category_score(Category.CHANCE), 25)

    def test_reject_invalid_joker_category_when_not_allowed(self):
        self.card.set_category_score(Category.YAHTZEE, None)
        # YAHTZEE of 6s, SIXES box still open → must use SIXES
        with self.assertRaises(InvalidCategoryError):
            self.card.set_category_score(Category.CHANCE, [6, 6, 6, 6, 6])

if __name__ == "__main__":
    unittest.main()
