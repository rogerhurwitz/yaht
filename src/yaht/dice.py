# src/yaht/dice.py
import random
from collections import Counter  # Added for frequency counting in map methods
from typing import Callable, TypeAlias

from yaht.category import Category
from yaht.exceptions import (  # Added DiceCountError and DieValueError for validation
    DiceCountError,
    DiceRollCountError,
    DiceRollIndexError,
    DieValueError,
)

# Imported for criteria checking (ensures we can call is_playable and related functions)
from yaht.playable import (  # Added to integrate with playable.py for meets_criteria
    _is_playable_standard_rules,
    is_playable,
)
from yaht.scorecard import ScorecardLike

DiceList: TypeAlias = list[int]


class DiceRoll:
    def __init__(self, dice_list: DiceList):
        """Validate dice_list in accord with Yahtzee rules and initialize class."""
        # Validate input per Yahtzee rules: exactly 5 dice, each with value 1-6
        if len(dice_list) != 5:
            raise DiceCountError(f"Invalid dice count: {len(dice_list)}. Must be exactly 5.")
        if not all(1 <= die <= 6 for die in dice_list):
            raise DieValueError("All dice values must be integers between 1 and 6.")
        # Store the validated dice list
        self._values = dice_list

    def map_value_to_count(self) -> dict[int, int]:
        """Return dict, keys: die value (1-6), values: count frequency."""
        count = Counter(self._values)
        # Ensure all keys from 1-6 are present, with 0 for missing values
        return {i: count.get(i, 0) for i in range(1, 7)}

    def map_count_to_values(self) -> dict[int, list[int]]:
        """Return dict, keys: count frequency (include 0), values: die values."""
        count = Counter(self._values)
        # Initialize result with keys 0-5 (max count is 5 for Yahtzee)
        result = {i: [] for i in range(6)}
        # Populate based on counts for each die value
        for val in range(1, 7):
            cnt = count.get(val, 0)
            result[cnt].append(val)
        return result

    def meets_criteria(self, category: Category, card: None | ScorecardLike = None) -> bool:
        """True if category criteria met else False. Apply joker rules if card is not None."""
        # If no card is provided, use standard rules without joker logic
        if card is None:
            return _is_playable_standard_rules(
                category, self._values, match_zero_playable=False
            )
        # If card is provided, use full is_playable to include joker rules
        else:
            return is_playable(category, self._values, card, match_zero_playable=False)


class Dice:
    def __init__(self, rng: Callable[[], int] = lambda: random.randint(1, 6)):
        """Initialize members and perform first roll for player."""
        self._rng = rng
        self._values = [0, 0, 0, 0, 0]
        self._roll_count = 0
        # Perform first roll automatically
        self.reroll([0, 1, 2, 3, 4])

    @property
    def values(self) -> list[int]:
        """Return list of die values for each of the 5 dice."""
        return self._values.copy()

    @property
    def roll_count(self) -> int:
        """Returns current number of rolls taken by player this turn."""
        return self._roll_count

    def reroll(self, indices: list[int]) -> None:
        """Re-roll dice specified by indices, others are keepers."""
        # Check if player has already rolled 3 times
        if self._roll_count >= 3:
            raise DiceRollCountError("Cannot roll more than 3 times per turn")

        # Check for OOB and duplicate indices. Indirectly catches len > 5
        seen: set[int] = set()
        for idx in indices:
            if idx < 0 or idx >= 5:
                raise DiceRollIndexError(f"Invalid die index: {idx}. Must be between 0 and 4")
            if idx in seen:
                raise DiceRollIndexError(f"Invalid die index: {idx}. Must not be a duplicate.")
            seen.add(idx)

        # Roll only the specified dice
        for idx in indices:
            self._values[idx] = self._rng()

        self._roll_count += 1
