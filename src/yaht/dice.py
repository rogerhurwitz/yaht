# src/yaht/dice.py
from collections import Counter
from typing import Any, Iterator

from yaht.category import Category
from yaht.exceptions import (
    DiceCountError,
    DieValueError,
)


class DiceRoll:
    def __init__(self, numbers: list[int]):
        """Validate dice_list in accord with Yahtzee rules and initialize class."""
        # Check if we have exactly 5 dice
        if len(numbers) != 5:
            raise DiceCountError(f"Invalid dice count: {len(numbers)}")

        # Check if all dice values are between 1 and 6
        if any(d < 1 or d > 6 for d in numbers):
            raise DieValueError("The value of all dice must be between 1 and 6.")

        # Copy to avoid risk that dice_list argument is later mutated by caller
        self._numbers = numbers.copy()

    def __repr__(self) -> str:
        """Return string representation of the dice roll."""
        return f"DiceRoll({self._numbers})"

    def __len__(self) -> int:
        """Return the number of dice (always 5 for Yahtzee)."""
        return len(self._numbers)

    def __eq__(self, other: Any) -> bool:
        """Check equality with another DiceRoll (order independent)."""
        if not isinstance(other, DiceRoll):
            return NotImplemented
        return sorted(self._numbers) == sorted(other._numbers)

    def __hash__(self) -> int:
        """Make DiceRoll hashable (useful for sets/dicts)."""
        return hash(tuple(sorted(self._numbers)))

    def __contains__(self, element: Category | int) -> bool:
        if isinstance(element, int):
            return element in self._numbers

        if element in Category.get_upper_categories() or element == Category.CHANCE:
            return True  # These categories are unconstrained (apart from joker rules)

        number_counts = Counter(self._numbers).values()
        sorted_numbers = sorted(self._numbers)

        if element == Category.THREE_OF_A_KIND:
            return max(number_counts) >= 3

        if element == Category.FOUR_OF_A_KIND:
            return max(number_counts) >= 4

        if element == Category.FULL_HOUSE:
            return sorted(number_counts) in [[2, 3], [5]]

        if element == Category.SMALL_STRAIGHT:
            straights = [{1, 2, 3, 4}, {2, 3, 4, 5}, {3, 4, 5, 6}]
            return any(set(self._numbers).issuperset(s) for s in straights)

        if element == Category.LARGE_STRAIGHT:
            return sorted_numbers in [[1, 2, 3, 4, 5], [2, 3, 4, 5, 6]]

        if element == Category.YAHTZEE:
            return max(number_counts) == 5

        return False

    def __getitem__(self, index: int) -> int:
        """Get number at specified index."""
        return self._numbers[index]

    def __iter__(self) -> Iterator[int]:
        """Iterate over dice numbers."""
        return iter(self._numbers)

    @property
    def numbers(self) -> list[int]:
        """Return a copy of the dice numbers list."""
        return self._numbers.copy()
