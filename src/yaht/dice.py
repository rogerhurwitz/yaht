# src/yaht/dice.py
import random
from typing import Any, Callable, Iterator, TypeAlias

from yaht.exceptions import (
    DiceCountError,
    DiceRollCountError,
    DiceRollIndexError,
    DieValueError,
)

DiceList: TypeAlias = list[int]


class DiceRoll:
    def __init__(self, dice_list: DiceList):
        """Validate dice_list in accord with Yahtzee rules and initialize class."""
        # Check if we have exactly 5 dice
        if len(dice_list) != 5:
            raise DiceCountError(f"Invalid dice count: {len(dice_list)}")

        # Check if all dice values are between 1 and 6
        if any(d < 1 or d > 6 for d in dice_list):
            raise DieValueError("The value of all dice must be between 1 and 6.")

        # Copy to avoid risk that dice_list argument is later mutated by caller
        self._dice = dice_list.copy()

    def __repr__(self) -> str:
        """Return string representation of the dice roll."""
        return f"DiceRoll({self._dice})"

    def __len__(self) -> int:
        """Return the number of dice (always 5 for Yahtzee)."""
        return len(self._dice)

    def __eq__(self, other: Any) -> bool:
        """Check equality with another DiceRoll (order independent)."""
        if not isinstance(other, DiceRoll):
            return NotImplemented
        return sorted(self._dice) == sorted(other._dice)

    def __hash__(self) -> int:
        """Make DiceRoll hashable (useful for sets/dicts)."""
        return hash(tuple(sorted(self._dice)))

    @property
    def dice(self) -> list[int]:
        """Return a copy of the dice list."""
        return self._dice.copy()

    @property
    def value_map(self) -> dict[int, int]:
        """Return dict, keys: die value (1-6), values; count frequency."""
        return {die_value: self._dice.count(die_value) for die_value in range(1, 7)}

    @property
    def count_map(self) -> dict[int, list[int]]:
        """Return dict, keys: count frequency (include 0), values: die values."""
        count_to_values_map: dict[int, list[int]] = {count: [] for count in range(0, 6)}
        for die_value, die_count in self.value_map.items():
            count_to_values_map[die_count].append(die_value)
        return count_to_values_map

    def __getitem__(self, index: int) -> int:
        """Get die value at specified index."""
        try:
            return self._dice[index]
        except IndexError as e:
            raise DiceRollIndexError(f"Index {index} out of range for dice roll") from e

    def __iter__(self) -> Iterator[int]:
        """Iterate over dice values."""
        return iter(self._dice)


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
