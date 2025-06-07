import unittest

from yaht.dice import Dice
from yaht.exceptions import DiceRollCountError, DiceRollIndexError


class TestDice(unittest.TestCase):
    def setUp(self):
        self.fixed_rng = lambda: 3  # Always rolls 3
        self.dice = Dice(rng=self.fixed_rng)

    def test_initial_roll_on_construction(self):
        self.assertEqual(self.dice.values, [3, 3, 3, 3, 3])
        self.assertEqual(self.dice.roll_count, 1)

    def test_reroll_updates_specified_indices(self):
        self.dice._values = [1, 2, 3, 4, 5]
        self.dice.reroll([0, 2, 4])
        self.assertEqual(self.dice.values, [3, 2, 3, 4, 3])  # 3 from fixed RNG
        self.assertEqual(self.dice.roll_count, 2)

    def test_reroll_does_not_affect_unlisted_indices(self):
        self.dice._values = [1, 2, 3, 4, 5]
        self.dice.reroll([1, 3])
        self.assertEqual(self.dice.values[0], 1)
        self.assertEqual(self.dice.values[2], 3)
        self.assertEqual(self.dice.values[4], 5)

    def test_reroll_limit_exceeded_raises(self):
        self.dice.reroll([0])  # second roll
        self.dice.reroll([1])  # third roll
        with self.assertRaises(DiceRollCountError):
            self.dice.reroll([2])

    def test_reroll_with_invalid_index_raises(self):
        with self.assertRaises(DiceRollIndexError):
            self.dice.reroll([-1])
        with self.assertRaises(DiceRollIndexError):
            self.dice.reroll([5])
        with self.assertRaises(DiceRollIndexError):
            self.dice.reroll([0, 6])

    def test_values_are_copied_not_referenced(self):
        values = self.dice.values
        values[0] = 99
        self.assertNotEqual(values, self.dice.values)

    def test_reroll_with_duplicate_indices(self):
        with self.assertRaises(DiceRollIndexError):
            self.dice.reroll([0, 1, 2, 0])

    def test_reroll_with_too_many_indices(self):
        with self.assertRaises(DiceRollIndexError):
            self.dice.reroll([0, 1, 2, 3, 4, 5])


if __name__ == "__main__":
    unittest.main()
