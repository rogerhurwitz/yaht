# src/yaht/dice.py
import random
from typing import Callable, TypeAlias

from yaht.category import Category
from yaht.exceptions import DiceRollCountError, DiceRollIndexError
from yaht.scorecard import ScorecardLike

DiceList: TypeAlias = list[int]


class DiceRoll:
    def __init__(self, dice_list: DiceList):
        """Validate dice_list in accord with Yahtzee rules and initialize class."""
        raise NotImplementedError()

    def map_value_to_count(self) -> dict[int, int]:
        """Return dict, keys: die value (1-6), values; count frequency."""
        raise NotImplementedError()

    def map_count_to_values(self) -> dict[int, list[int]]:
        """Return dict, keys: count frequency (include 0), values: die values."""
        raise NotImplementedError()

    def meets_criteria(self, category: Category, card: None | ScorecardLike = None) -> bool:
        """True if category criteria met else False. Apply joker rules if card is not None."""
        raise NotImplementedError()


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
