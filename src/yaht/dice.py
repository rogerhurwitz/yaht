# src/yaht/dice.py
import random
from typing import Callable

from yaht.exceptions import DiceRollCountError, DiceRollIndexError


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

        # Roll the specified dice
        for idx in indices:
            self._values[idx] = self._rng()

        # Increment roll count
        self._roll_count += 1
