import unittest

from yaht.category import Category
from yaht.dice import DiceRoll

# from yaht.exceptions import InvalidDiceError  # Assume this or ValueError used
# from yaht.scorecard import ScorecardLike  # Or use Protocol if applicable


class MockScorecard:
    def __init__(self, scored: dict[Category, int | None]):
        self.category_scores: dict[Category, int | None] = {
            category: None for category in Category
        }
        for k, v in scored.items():
            self.category_scores[k] = v

    def __getitem__(self, category: Category) -> int | None:
        return self.category_scores[category]

    def is_scored(self, category: Category) -> bool:
        return self.category_scores[category] is not None


class TestDiceRoll(unittest.TestCase):
    def test_constructor_valid(self):
        DiceRoll([1, 2, 3, 4, 5])  # Should not raise

    def test_constructor_invalid_length(self):
        with self.assertRaises(ValueError):
            DiceRoll([1, 2, 3, 4])

    def test_constructor_invalid_values(self):
        with self.assertRaises(ValueError):
            DiceRoll([1, 2, 3, 4, 7])

    def test_map_value_to_count(self):
        roll = DiceRoll([2, 2, 3, 4, 4])
        result = roll.map_value_to_count()
        self.assertEqual(result[2], 2)
        self.assertEqual(result[3], 1)
        self.assertEqual(result[4], 2)
        self.assertEqual(result[1], 0)
        self.assertEqual(result[5], 0)
        self.assertEqual(result[6], 0)

    def test_map_count_to_values(self):
        roll = DiceRoll([3, 3, 3, 1, 6])
        result = roll.map_count_to_values()
        self.assertIn(3, result)
        self.assertIn(1, result)
        self.assertIn(0, result)
        self.assertCountEqual(result[3], [3])
        self.assertCountEqual(result[1], [1, 6])
        self.assertTrue(
            all(val in range(1, 7) for count_list in result.values() for val in count_list)
        )

    def test_meets_criteria_yahtzee(self):
        roll = DiceRoll([4, 4, 4, 4, 4])
        self.assertTrue(roll.meets_criteria(Category.YAHTZEE))

    def test_meets_criteria_full_house(self):
        roll = DiceRoll([2, 2, 3, 3, 3])
        self.assertTrue(roll.meets_criteria(Category.FULL_HOUSE))

    def test_meets_criteria_chance(self):
        roll = DiceRoll([1, 2, 3, 4, 6])
        self.assertTrue(roll.meets_criteria(Category.CHANCE))

    # --- Joker Rule Tests ---

    def test_joker_rule_allowed_in_lower_section(self):
        roll = DiceRoll([5, 5, 5, 5, 5])
        card = MockScorecard(
            {
                Category.YAHTZEE: 50,
                Category.FIVES: 25,  # FIVES filled, so Joker rule applies
            }
        )
        self.assertTrue(roll.meets_criteria(Category.FULL_HOUSE, card))

    def test_joker_rule_requires_upper_filled(self):
        roll = DiceRoll([3, 3, 3, 3, 3])
        card = MockScorecard(
            {
                Category.YAHTZEE: 50,
                # THREES not filled → must be used there
            }
        )
        self.assertTrue(roll.meets_criteria(Category.THREES, card))
        self.assertFalse(roll.meets_criteria(Category.LARGE_STRAIGHT, card))

    def test_joker_rule_blocked_when_yahtzee_not_scored(self):
        roll = DiceRoll([6, 6, 6, 6, 6])
        card = MockScorecard({Category.SIXES: 30})
        self.assertFalse(roll.meets_criteria(Category.FULL_HOUSE, card))

    def test_joker_rule_applies_to_small_straight(self):
        roll = DiceRoll([1, 1, 1, 1, 1])
        card = MockScorecard({Category.YAHTZEE: 50, Category.ACES: 5})
        self.assertTrue(roll.meets_criteria(Category.SMALL_STRAIGHT, card))

    def test_joker_rule_requires_yahtzee_scored_with_nonzero(self):
        roll = DiceRoll([2, 2, 2, 2, 2])
        card = MockScorecard(
            {
                Category.YAHTZEE: 0,  # Scored with 0 → joker rule does not apply
                Category.TWOS: 10,
            }
        )
        self.assertFalse(roll.meets_criteria(Category.FULL_HOUSE, card))


if __name__ == "__main__":
    unittest.main()
