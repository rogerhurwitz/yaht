import random
from typing import Callable

from yaht.exceptions import DiceRollCountError, DiceRollIndexError


class Dice:
    def __init__(self, rng: Callable[[], int] = lambda: random.randint(1, 6)):
        """Initialize members and perform first roll for player."""

    @property
    def values(self) -> list[int]:
        """Return list of die values for each of the 5 dice."""

    @property
    def roll_count(self) -> int:
        """Returns number of rolls taken by player this turn."""

    def reroll(self, indices: list[int]) -> None:
        """Re-roll dice specified by indices, others are keepers."""
