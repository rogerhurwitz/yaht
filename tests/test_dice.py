import unittest

from yaht.dice import DiceRoll
from yaht.exceptions import (
    DiceCountError,
    DiceRollIndexError,
    DieValueError,
)


class TestDiceRollInitialization(unittest.TestCase):
    """Tests for DiceRoll initialization and validation."""

    def test_valid_initialization(self):
        """Test valid dice roll initialization."""
        dice = [1, 2, 3, 4, 5]
        roll = DiceRoll(dice)
        self.assertEqual(roll.dice, dice)

    def test_initialization_copies_input(self):
        """Test that initialization creates a copy of input list."""
        dice = [1, 2, 3, 4, 5]
        roll = DiceRoll(dice)
        dice[0] = 6  # Modify original
        self.assertEqual(roll.dice[0], 1)  # Should be unchanged

    def test_invalid_dice_count_too_few(self):
        """Test error for too few dice."""
        with self.assertRaises(DiceCountError) as cm:
            DiceRoll([1, 2, 3, 4])
        self.assertIn("Invalid dice count: 4", str(cm.exception))

    def test_invalid_dice_count_too_many(self):
        """Test error for too many dice."""
        with self.assertRaises(DiceCountError) as cm:
            DiceRoll([1, 2, 3, 4, 5, 6])
        self.assertIn("Invalid dice count: 6", str(cm.exception))

    def test_invalid_dice_count_empty(self):
        """Test error for empty dice list."""
        with self.assertRaises(DiceCountError):
            DiceRoll([])

    def test_invalid_die_value_too_low(self):
        """Test error for die value below 1."""
        with self.assertRaises(DieValueError) as cm:
            DiceRoll([0, 2, 3, 4, 5])
        self.assertIn("The value of all dice must be between 1 and 6", str(cm.exception))

    def test_invalid_die_value_too_high(self):
        """Test error for die value above 6."""
        with self.assertRaises(DieValueError):
            DiceRoll([1, 2, 3, 4, 7])

    def test_invalid_die_value_negative(self):
        """Test error for negative die value."""
        with self.assertRaises(DieValueError):
            DiceRoll([-1, 2, 3, 4, 5])

    def test_multiple_invalid_die_values(self):
        """Test error when multiple dice have invalid values."""
        with self.assertRaises(DieValueError):
            DiceRoll([0, 2, 7, 4, 8])


class TestDiceRollStringRepresentation(unittest.TestCase):
    """Tests for string representation methods."""

    def test_repr(self):
        """Test __repr__ method."""
        roll = DiceRoll([1, 2, 3, 4, 5])
        self.assertEqual(repr(roll), "DiceRoll([1, 2, 3, 4, 5])")

    def test_repr_with_duplicates(self):
        """Test __repr__ with duplicate dice values."""
        roll = DiceRoll([1, 1, 3, 3, 5])
        self.assertEqual(repr(roll), "DiceRoll([1, 1, 3, 3, 5])")


class TestDiceRollProperties(unittest.TestCase):
    """Tests for DiceRoll properties."""

    def test_dice_property_returns_copy(self):
        """Test that dice property returns a copy."""
        roll = DiceRoll([1, 2, 3, 4, 5])
        dice_copy = roll.dice
        dice_copy[0] = 6
        self.assertEqual(roll.dice[0], 1)  # Original unchanged

    def test_len(self):
        """Test __len__ method."""
        roll = DiceRoll([1, 2, 3, 4, 5])
        self.assertEqual(len(roll), 5)


class TestDiceRollValueMap(unittest.TestCase):
    """Tests for value_map property."""

    def test_value_map_all_different(self):
        """Test value_map when all dice are different."""
        roll = DiceRoll([1, 2, 3, 4, 5])
        expected = {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 0}
        self.assertEqual(roll.value_map, expected)

    def test_value_map_with_pairs(self):
        """Test value_map with pairs."""
        roll = DiceRoll([1, 1, 3, 4, 5])
        expected = {1: 2, 2: 0, 3: 1, 4: 1, 5: 1, 6: 0}
        self.assertEqual(roll.value_map, expected)

    def test_value_map_three_of_kind(self):
        """Test value_map with three of a kind."""
        roll = DiceRoll([2, 2, 2, 4, 5])
        expected = {1: 0, 2: 3, 3: 0, 4: 1, 5: 1, 6: 0}
        self.assertEqual(roll.value_map, expected)

    def test_value_map_four_of_kind(self):
        """Test value_map with four of a kind."""
        roll = DiceRoll([3, 3, 3, 3, 5])
        expected = {1: 0, 2: 0, 3: 4, 4: 0, 5: 1, 6: 0}
        self.assertEqual(roll.value_map, expected)

    def test_value_map_yahtzee(self):
        """Test value_map with Yahtzee (all same)."""
        roll = DiceRoll([4, 4, 4, 4, 4])
        expected = {1: 0, 2: 0, 3: 0, 4: 5, 5: 0, 6: 0}
        self.assertEqual(roll.value_map, expected)

    def test_value_map_full_house(self):
        """Test value_map with full house."""
        roll = DiceRoll([2, 2, 2, 5, 5])
        expected = {1: 0, 2: 3, 3: 0, 4: 0, 5: 2, 6: 0}
        self.assertEqual(roll.value_map, expected)


class TestDiceRollCountMap(unittest.TestCase):
    """Tests for count_map property."""

    def test_count_map_all_different(self):
        """Test count_map when all dice are different."""
        roll = DiceRoll([1, 2, 3, 4, 5])
        expected: dict[int, list[int]] = {
            0: [6],  # No dice show 6
            1: [1, 2, 3, 4, 5],  # One each of 1,2,3,4,5
            2: [],  # No pairs
            3: [],  # No three of a kind
            4: [],  # No four of a kind
            5: [],  # No Yahtzee
        }
        self.assertEqual(roll.count_map, expected)

    def test_count_map_with_pair(self):
        """Test count_map with a pair."""
        roll = DiceRoll([1, 1, 3, 4, 5])
        expected: dict[int, list[int]] = {
            0: [2, 6],  # No dice show 2 or 6
            1: [3, 4, 5],  # One each of 3,4,5
            2: [1],  # Pair of 1s
            3: [],
            4: [],
            5: [],
        }
        self.assertEqual(roll.count_map, expected)

    def test_count_map_three_of_kind(self):
        """Test count_map with three of a kind."""
        roll = DiceRoll([2, 2, 2, 4, 5])
        expected: dict[int, list[int]] = {
            0: [1, 3, 6],  # No dice show 1, 3, or 6
            1: [4, 5],  # One each of 4,5
            2: [],  # No pairs
            3: [2],  # Three 2s
            4: [],
            5: [],
        }
        self.assertEqual(roll.count_map, expected)

    def test_count_map_yahtzee(self):
        """Test count_map with Yahtzee."""
        roll = DiceRoll([4, 4, 4, 4, 4])
        expected: dict[int, list[int]] = {
            0: [1, 2, 3, 5, 6],  # No dice show 1,2,3,5,6
            1: [],
            2: [],
            3: [],
            4: [],
            5: [4],  # All five dice show 4
        }
        self.assertEqual(roll.count_map, expected)


class TestDiceRollIndexing(unittest.TestCase):
    """Tests for indexing operations."""

    def test_getitem_valid_indices(self):
        """Test __getitem__ with valid indices."""
        roll = DiceRoll([1, 2, 3, 4, 5])
        self.assertEqual(roll[0], 1)
        self.assertEqual(roll[1], 2)
        self.assertEqual(roll[4], 5)

    def test_getitem_negative_indices(self):
        """Test __getitem__ with negative indices."""
        roll = DiceRoll([1, 2, 3, 4, 5])
        self.assertEqual(roll[-1], 5)
        self.assertEqual(roll[-5], 1)

    def test_getitem_index_out_of_range_positive(self):
        """Test __getitem__ with positive index out of range."""
        roll = DiceRoll([1, 2, 3, 4, 5])
        with self.assertRaises(DiceRollIndexError) as cm:
            _ = roll[5]
        self.assertIn("Index 5 out of range", str(cm.exception))

    def test_getitem_index_out_of_range_negative(self):
        """Test __getitem__ with negative index out of range."""
        roll = DiceRoll([1, 2, 3, 4, 5])
        with self.assertRaises(DiceRollIndexError) as cm:
            _ = roll[-6]
        self.assertIn("Index -6 out of range", str(cm.exception))


class TestDiceRollIteration(unittest.TestCase):
    """Tests for iteration operations."""

    def test_iteration(self):
        """Test __iter__ method."""
        dice = [1, 2, 3, 4, 5]
        roll = DiceRoll(dice)
        result = list(roll)
        self.assertEqual(result, dice)

    def test_iteration_with_duplicates(self):
        """Test iteration with duplicate values."""
        dice = [1, 1, 3, 3, 5]
        roll = DiceRoll(dice)
        result = list(roll)
        self.assertEqual(result, dice)

    def test_for_loop_iteration(self):
        """Test iteration in for loop."""
        dice = [1, 2, 3, 4, 5]
        roll = DiceRoll(dice)
        result: list[int] = []
        for die in roll:
            result.append(die)
        self.assertEqual(result, dice)


class TestDiceRollEquality(unittest.TestCase):
    """Tests for equality operations."""

    def test_equality_same_order(self):
        """Test equality with same dice in same order."""
        roll1 = DiceRoll([1, 2, 3, 4, 5])
        roll2 = DiceRoll([1, 2, 3, 4, 5])
        self.assertEqual(roll1, roll2)

    def test_equality_different_order(self):
        """Test equality with same dice in different order."""
        roll1 = DiceRoll([1, 2, 3, 4, 5])
        roll2 = DiceRoll([5, 4, 3, 2, 1])
        self.assertEqual(roll1, roll2)

    def test_equality_with_duplicates(self):
        """Test equality with duplicate values."""
        roll1 = DiceRoll([1, 1, 3, 3, 5])
        roll2 = DiceRoll([3, 1, 5, 3, 1])
        self.assertEqual(roll1, roll2)

    def test_inequality_different_dice(self):
        """Test inequality with different dice."""
        roll1 = DiceRoll([1, 2, 3, 4, 5])
        roll2 = DiceRoll([1, 2, 3, 4, 6])
        self.assertNotEqual(roll1, roll2)

    def test_equality_with_non_diceroll(self):
        """Test equality comparison with non-DiceRoll object."""
        roll = DiceRoll([1, 2, 3, 4, 5])
        self.assertNotEqual(roll, [1, 2, 3, 4, 5])
        self.assertNotEqual(roll, "not a dice roll")
        self.assertNotEqual(roll, 42)


class TestDiceRollHashing(unittest.TestCase):
    """Tests for hashing operations."""

    def test_hash_same_dice_same_order(self):
        """Test hash for identical dice rolls."""
        roll1 = DiceRoll([1, 2, 3, 4, 5])
        roll2 = DiceRoll([1, 2, 3, 4, 5])
        self.assertEqual(hash(roll1), hash(roll2))

    def test_hash_same_dice_different_order(self):
        """Test hash for same dice in different order."""
        roll1 = DiceRoll([1, 2, 3, 4, 5])
        roll2 = DiceRoll([5, 4, 3, 2, 1])
        self.assertEqual(hash(roll1), hash(roll2))

    def test_hash_different_dice(self):
        """Test hash for different dice (should likely be different)."""
        roll1 = DiceRoll([1, 2, 3, 4, 5])
        roll2 = DiceRoll([1, 2, 3, 4, 6])
        # Note: Hash collision is possible but very unlikely
        self.assertNotEqual(hash(roll1), hash(roll2))

    def test_hashable_in_set(self):
        """Test that DiceRoll can be used in sets."""
        roll1 = DiceRoll([1, 2, 3, 4, 5])
        roll2 = DiceRoll([5, 4, 3, 2, 1])  # Same dice, different order
        roll3 = DiceRoll([1, 2, 3, 4, 6])  # Different dice

        dice_set = {roll1, roll2, roll3}
        self.assertEqual(len(dice_set), 2)  # roll1 and roll2 are equal

    def test_hashable_as_dict_key(self):
        """Test that DiceRoll can be used as dictionary key."""
        roll1 = DiceRoll([1, 2, 3, 4, 5])
        roll2 = DiceRoll([5, 4, 3, 2, 1])

        dice_dict = {roll1: "straight"}
        dice_dict[roll2] = "also straight"  # Should overwrite

        self.assertEqual(len(dice_dict), 1)
        self.assertEqual(dice_dict[roll1], "also straight")


class TestDiceRollEdgeCases(unittest.TestCase):
    """Tests for edge cases and boundary conditions."""

    def test_all_ones(self):
        """Test with all dice showing 1."""
        roll = DiceRoll([1, 1, 1, 1, 1])
        self.assertEqual(roll.value_map[1], 5)
        self.assertEqual(roll.count_map[5], [1])

    def test_all_sixes(self):
        """Test with all dice showing 6."""
        roll = DiceRoll([6, 6, 6, 6, 6])
        self.assertEqual(roll.value_map[6], 5)
        self.assertEqual(roll.count_map[5], [6])

    def test_mixed_extreme_values(self):
        """Test with mix of 1s and 6s."""
        roll = DiceRoll([1, 1, 6, 6, 6])
        expected_value_map = {1: 2, 2: 0, 3: 0, 4: 0, 5: 0, 6: 3}
        self.assertEqual(roll.value_map, expected_value_map)

    def test_property_recalculation(self):
        """Test that properties are recalculated correctly on each access."""
        dice = [1, 2, 3, 4, 5]
        roll = DiceRoll(dice)

        # Access properties multiple times
        map1 = roll.value_map
        map2 = roll.value_map
        count1 = roll.count_map
        count2 = roll.count_map

        # Should be equal but potentially different objects
        self.assertEqual(map1, map2)
        self.assertEqual(count1, count2)


if __name__ == "__main__":
    # Run all tests
    unittest.main(verbosity=2)
