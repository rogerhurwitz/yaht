import unittest
from typing import cast

from yaht.category import Category
from yaht.dicetypes import DiceRoll
from yaht.exceptions import (
    CategoryAlreadyScored,
    DiceCountError,
    DieValueError,
    InvalidCategoryError,
)
from yaht.scorecard import Scorecard
from yaht.scorecheck import calculate_combo_score, is_combo_scoreable


class BaseScorecardTest(unittest.TestCase):
    def setUp(self):
        self.card = Scorecard()

    def assert_score(self, category: Category, dice: DiceRoll, expected: int):
        self.card.set_category_score(category, dice)
        self.assertEqual(self.card.category_scores[category], expected)


class TestUpperSection(BaseScorecardTest):
    def test_aces_scoring(self):
        self.assert_score(Category.ACES, DiceRoll([1, 1, 2, 3, 4]), 2)

    def test_zero_score_when_no_dice_match(self):
        self.assert_score(Category.TWOS, DiceRoll([1, 1, 3, 4, 5]), 0)

    def test_upper_bonus_awarded(self):
        for category in Category.get_upper_categories():
            assert category.die_number is not None
            self.card.set_category_score(category, DiceRoll([category.die_number] * 5))
        self.assertGreaterEqual(self.card.get_card_score(), 63 + 35)  # includes bonus


class TestLowerSection(BaseScorecardTest):
    def test_three_of_a_kind_valid(self):
        self.assert_score(Category.THREE_OF_A_KIND, DiceRoll([2, 2, 2, 4, 5]), 15)

    def test_full_house_scoring(self):
        self.assert_score(Category.FULL_HOUSE, DiceRoll([3, 3, 3, 6, 6]), 25)

    def test_small_straight_valid(self):
        self.assert_score(Category.SMALL_STRAIGHT, DiceRoll([1, 2, 3, 4, 6]), 30)

    def test_large_straight_valid(self):
        self.assert_score(Category.LARGE_STRAIGHT, DiceRoll([2, 3, 4, 5, 6]), 40)

    def test_yahtzee(self):
        self.assert_score(Category.YAHTZEE, DiceRoll([5, 5, 5, 5, 5]), 50)


class TestValidation(BaseScorecardTest):
    def test_invalid_dice_count(self):
        with self.assertRaises(DiceCountError):
            self.card.set_category_score(Category.FOURS, DiceRoll([4, 4, 4]))

    def test_invalid_die_value(self):
        with self.assertRaises(DieValueError):
            self.card.set_category_score(Category.FIVES, DiceRoll([5, 5, 5, 5, 7]))

    def test_category_already_scored(self):
        self.card.set_category_score(Category.THREES, DiceRoll([3, 3, 3, 2, 1]))
        with self.assertRaises(CategoryAlreadyScored):
            self.card.set_category_score(Category.THREES, DiceRoll([3, 3, 3, 3, 3]))

    def test_invalid_category(self):
        self.assertEqual(self.card.category_scores.get(cast(Category, "INVALID")), None)


class TestBonuses(BaseScorecardTest):
    def test_yahtzee_bonus_applied(self):
        self.card.set_category_score(Category.YAHTZEE, DiceRoll([6, 6, 6, 6, 6]))
        self.card.set_category_score(Category.SIXES, DiceRoll([6, 6, 6, 6, 6]))
        self.card.set_category_score(Category.THREE_OF_A_KIND, DiceRoll([6, 6, 6, 6, 6]))
        self.assertEqual(self.card.yahtzee_bonus_count, 2)

    def test_joker_rule_blocks_wrong_category(self):
        self.card.set_category_score(Category.YAHTZEE, DiceRoll([3, 3, 3, 3, 3]))
        with self.assertRaises(InvalidCategoryError):
            self.card.set_category_score(Category.FOUR_OF_A_KIND, DiceRoll([3, 3, 3, 3, 3]))

    def test_zero_category(self):
        self.card.zero_category(Category.CHANCE, DiceRoll([1, 2, 3, 4, 5]))
        self.assertEqual(self.card.category_scores[Category.CHANCE], 0)

        with self.assertRaises(CategoryAlreadyScored):
            self.card.zero_category(Category.CHANCE, DiceRoll([1, 2, 3, 4, 5]))


class TestScoringModule(BaseScorecardTest):
    def test_invalid_category(self):
        with self.assertRaises(Exception):
            calculate_combo_score(cast(Category, "INVALID"), DiceRoll([1, 2, 3, 4, 5]))


class TestOriginalMetrics(BaseScorecardTest):
    def test_scorecard_type(self):
        """Confirm that scorecard is an instance of Scorecard."""
        self.assertIsInstance(self.card, Scorecard)

    def test_initial_score(self):
        """Confirm that scorecard initial score total is zero."""
        self.assertEqual(self.card.get_card_score(), 0)

    def test_yahtzee_scoring(self):
        self.card.set_category_score(Category.YAHTZEE, DiceRoll([6, 6, 6, 6, 6]))
        self.assertEqual(self.card.category_scores[Category.YAHTZEE], 50)

    def test_chance_scoring(self):
        self.card.set_category_score(Category.CHANCE, DiceRoll([1, 2, 3, 4, 5]))
        self.assertEqual(self.card.category_scores[Category.CHANCE], 15)

    def test_null_dice_sets_zero(self):
        self.card.zero_category(Category.FIVES, DiceRoll([1, 2, 3, 4, 5]))
        self.assertEqual(self.card.category_scores[Category.FIVES], 0)

    def test_upper_section_bonus_awarded(self):
        # Score exactly 63: three of each 1–6
        self.card.set_category_score(Category.ACES, DiceRoll([1, 1, 1, 2, 3]))
        self.card.set_category_score(Category.TWOS, DiceRoll([2, 2, 2, 1, 3]))
        self.card.set_category_score(Category.THREES, DiceRoll([3, 3, 3, 2, 1]))
        self.card.set_category_score(Category.FOURS, DiceRoll([4, 4, 4, 1, 2]))
        self.card.set_category_score(Category.FIVES, DiceRoll([5, 5, 5, 1, 2]))
        self.card.set_category_score(Category.SIXES, DiceRoll([6, 6, 6, 1, 2]))
        total = self.card.get_card_score()
        self.assertGreaterEqual(total, 63 + 35)

    def test_joker_rule_used_when_yahtzee_zeroed(self):
        # First YAHTZEE is zeroed
        self.card.zero_category(Category.YAHTZEE, DiceRoll([1, 2, 3, 4, 5]))
        # Later roll a Yahtzee again (e.g., five 4s)
        self.card.set_category_score(Category.FOURS, DiceRoll([4, 4, 4, 4, 4]))
        self.assertEqual(self.card.category_scores[Category.FOURS], 20)

    def test_joker_rule_applies_to_lower_section_if_upper_filled(self):
        # Zero YAHTZEE and fill FOURS
        self.card.zero_category(Category.YAHTZEE, DiceRoll([1, 2, 3, 4, 5]))
        self.card.set_category_score(Category.FOURS, DiceRoll([4, 4, 2, 1, 1]))  # FOURS = 8
        # Now roll five 4s again
        self.card.set_category_score(Category.FULL_HOUSE, DiceRoll([4, 4, 4, 4, 4]))
        self.assertEqual(self.card.category_scores[Category.FULL_HOUSE], 25)

    def test_joker_rule_fallback_zero(self):
        # Zero YAHTZEE and fill all legal options
        self.card.zero_category(Category.YAHTZEE, DiceRoll([1, 2, 3, 4, 5]))
        self.card.set_category_score(Category.FOURS, DiceRoll([4, 4, 2, 1, 1]))
        self.card.set_category_score(Category.FULL_HOUSE, DiceRoll([2, 2, 3, 3, 3]))
        self.card.set_category_score(Category.THREE_OF_A_KIND, DiceRoll([2, 2, 2, 4, 5]))
        self.card.set_category_score(Category.FOUR_OF_A_KIND, DiceRoll([6, 6, 6, 6, 3]))
        self.card.set_category_score(Category.SMALL_STRAIGHT, DiceRoll([1, 2, 3, 4, 6]))
        self.card.set_category_score(Category.LARGE_STRAIGHT, DiceRoll([2, 3, 4, 5, 6]))
        self.card.set_category_score(Category.CHANCE, DiceRoll([1, 1, 1, 2, 3]))
        # Now joker forced to fill a zero in an upper section box
        with self.assertRaises(CategoryAlreadyScored):
            self.card.set_category_score(Category.FOURS, DiceRoll([4, 4, 4, 4, 4]))

    def test_reject_illegal_joker_category(self):
        # Zero out the YAHTZEE box
        self.card.zero_category(Category.YAHTZEE, DiceRoll([1, 2, 3, 4, 5]))
        # Fill required Upper Section box (e.g., FOURS)
        self.card.set_category_score(Category.FOURS, DiceRoll([4, 4, 1, 2, 3]))
        # Fill all Lower Section joker targets
        self.card.set_category_score(Category.FULL_HOUSE, DiceRoll([3, 3, 3, 2, 2]))
        self.card.set_category_score(Category.THREE_OF_A_KIND, DiceRoll([2, 2, 2, 4, 5]))
        self.card.set_category_score(Category.FOUR_OF_A_KIND, DiceRoll([6, 6, 6, 6, 1]))
        self.card.set_category_score(Category.SMALL_STRAIGHT, DiceRoll([1, 2, 3, 4, 5]))
        self.card.set_category_score(Category.LARGE_STRAIGHT, DiceRoll([2, 3, 4, 5, 6]))
        self.card.set_category_score(Category.CHANCE, DiceRoll([1, 1, 3, 4, 6]))
        # Try to place a Yahtzee of 4s into Full House again (should fail)
        with self.assertRaises(CategoryAlreadyScored):
            self.card.set_category_score(Category.FULL_HOUSE, DiceRoll([4, 4, 4, 4, 4]))

    def test_allow_valid_joker_category_when_upper_box_taken(self):
        self.card.zero_category(Category.YAHTZEE, DiceRoll([1, 2, 3, 4, 5]))
        self.card.set_category_score(Category.FIVES, DiceRoll([5, 5, 1, 2, 3]))
        # YAHTZEE of 5s, valid Joker placement in Chance
        self.card.set_category_score(Category.CHANCE, DiceRoll([5, 5, 5, 5, 5]))
        self.assertEqual(self.card.category_scores[Category.CHANCE], 25)

    def test_reject_invalid_joker_category_when_not_allowed(self):
        self.card.zero_category(Category.YAHTZEE, DiceRoll([1, 2, 3, 4, 5]))
        # YAHTZEE of 6s, SIXES box still open → must use SIXES
        with self.assertRaises(InvalidCategoryError):
            self.card.set_category_score(Category.CHANCE, DiceRoll([6, 6, 6, 6, 6]))


class TestGetUnscoredCategoriees(BaseScorecardTest):
    def setUp(self):
        self.allcats = [cat for cat in Category]
        super().setUp()

    def test_no_scored(self):
        unscored = self.card.get_unscored_categories()
        self.assertEqual(set(unscored), set(self.allcats))

    def test_one_scored(self):
        self.card.zero_category(Category.ACES, DiceRoll([1, 2, 3, 4, 5]))
        unscored = self.card.get_unscored_categories()
        self.assertFalse(Category.ACES in unscored)
        self.assertEqual(len(unscored), len(self.allcats) - 1)

    def test_two_scored(self):
        self.card.zero_category(Category.ACES, DiceRoll([1, 2, 3, 4, 5]))
        self.card.zero_category(Category.YAHTZEE, DiceRoll([1, 2, 3, 4, 5]))
        unscored = self.card.get_unscored_categories()
        self.assertFalse(Category.ACES in unscored)
        self.assertFalse(Category.YAHTZEE in unscored)
        self.assertEqual(len(unscored), len(self.allcats) - 2)

    def test_all_scored(self):
        for cat in Category:
            self.card.zero_category(cat, DiceRoll([1, 2, 3, 4, 5]))
        unscored = self.card.get_unscored_categories()
        self.assertCountEqual(unscored, [])


# Update the relevant tests to reflect that all unscored Upper Section categories are playable
class TestGetPlayableCategories(BaseScorecardTest):
    def test_upper_section_and_small_straight(self):
        dice = DiceRoll([1, 2, 3, 4, 6])
        expected = {
            Category.ACES,
            Category.TWOS,
            Category.THREES,
            Category.FOURS,
            Category.FIVES,  # now explicitly valid even though score would be 0
            Category.SIXES,
            Category.SMALL_STRAIGHT,
            Category.CHANCE,
        }
        playable = [cat for cat in Category if is_combo_scoreable(cat, dice, self.card)]
        self.assertEqual(set(playable), expected)

    def test_three_of_a_kind_and_upper_options(self):
        dice = DiceRoll([5, 5, 5, 2, 3])
        expected = {
            Category.THREE_OF_A_KIND,
            Category.FIVES,
            Category.TWOS,
            Category.THREES,
            Category.ACES,  # valid even if it would score 0
            Category.FOURS,
            Category.SIXES,
            Category.CHANCE,
        }
        playable = [cat for cat in Category if is_combo_scoreable(cat, dice, self.card)]
        self.assertEqual(set(playable), expected)

    def test_full_house_included(self):
        dice = DiceRoll([3, 3, 3, 6, 6])
        expected = {
            Category.FULL_HOUSE,
            Category.THREE_OF_A_KIND,
            Category.THREES,
            Category.SIXES,
            Category.ACES,
            Category.TWOS,
            Category.FOURS,
            Category.FIVES,
            Category.CHANCE,
        }
        playable = [cat for cat in Category if is_combo_scoreable(cat, dice, self.card)]
        self.assertEqual(set(playable), expected)

    def test_yahtzee_joker_rule_behavior(self):
        self.card.set_category_score(Category.YAHTZEE, DiceRoll([6, 6, 6, 6, 6]))
        dice = DiceRoll([6, 6, 6, 6, 6])

        # Case 1: SIXES is open — must use SIXES
        expected = {Category.SIXES}
        playable = [cat for cat in Category if is_combo_scoreable(cat, dice, self.card)]
        self.assertEqual(set(playable), expected)

        # Case 2: SIXES scored — Joker rules allow specific Lower categories
        self.card.set_category_score(Category.SIXES, DiceRoll([6, 6, 6, 6, 6]))
        expected = {
            Category.THREE_OF_A_KIND,
            Category.FOUR_OF_A_KIND,
            Category.FULL_HOUSE,
            Category.SMALL_STRAIGHT,
            Category.LARGE_STRAIGHT,
            Category.CHANCE,
        }
        playable = [cat for cat in Category if is_combo_scoreable(cat, dice, self.card)]
        self.assertEqual(set(playable), expected)

    def test_category_already_scored_excluded(self):
        self.card.set_category_score(Category.FIVES, DiceRoll([5, 5, 5, 2, 3]))
        dice = DiceRoll([5, 5, 5, 2, 3])
        playable = [cat for cat in Category if is_combo_scoreable(cat, dice, self.card)]
        self.assertNotIn(Category.FIVES, playable)

    def test_unplayable_combo_limited_options(self):
        dice = DiceRoll([1, 1, 2, 2, 3])
        expected = {
            Category.ACES,
            Category.TWOS,
            Category.THREES,
            Category.FOURS,
            Category.FIVES,
            Category.SIXES,
            Category.CHANCE,
        }
        playable = [cat for cat in Category if is_combo_scoreable(cat, dice, self.card)]
        self.assertEqual(set(playable), expected)


class TestPerfectGame(unittest.TestCase):
    class TestPerfectGame(unittest.TestCase):
        def test_perfect_yahtzee_game_scores_1575(self):
            card = Scorecard()

            # Step 1: Score YAHTZEE with DiceRoll([6,6,6,6,6])
            sixes = [6] * 5
            card.set_category_score(Category.YAHTZEE, DiceRoll(sixes))

            # Step 2: Score SIXES immediately (required by Joker rule)
            card.set_category_score(Category.SIXES, DiceRoll(sixes))

            # Step 3: Score remaining upper categories with matching Yahtzees
            upper_map = {
                1: Category.ACES,
                2: Category.TWOS,
                3: Category.THREES,
                4: Category.FOURS,
                5: Category.FIVES,
            }
            for face in range(1, 6):  # Already did SIXES
                dice = [face] * 5
                card.set_category_score(upper_map[face], DiceRoll(dice))

            # Step 4: Score lower categories using Joker logic
            lower_categories = [
                Category.FULL_HOUSE,  # 25
                Category.SMALL_STRAIGHT,  # 30
                Category.LARGE_STRAIGHT,  # 40
                Category.THREE_OF_A_KIND,  # 30 (sum)
                Category.FOUR_OF_A_KIND,  # 30 (sum)
                Category.CHANCE,  # 30 (sum)
            ]
            face_cycle = [1, 2, 3, 4, 5, 6]
            for cat, face in zip(lower_categories, face_cycle):
                card.set_category_score(cat, DiceRoll([face] * 5))

            # Final assertion
            self.assertEqual(
                card.get_card_score(), 1575, f"Expected 1575, got {card.get_card_score()}"
            )


if __name__ == "__main__":
    unittest.main()
