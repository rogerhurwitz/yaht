from enum import Enum, auto

class Category(Enum):
    ACES = auto()
    TWOS = auto()
    THREES = auto()
    FOURS = auto()
    FIVES = auto()
    SIXES = auto()
    THREE_OF_A_KIND = auto()
    FOUR_OF_A_KIND = auto()
    FULL_HOUSE = auto()
    SMALL_STRAIGHT = auto()
    LARGE_STRAIGHT = auto()
    YAHTZEE = auto()
    CHANCE = auto()

class Scorecard:
    """Tracks the score for a single player."""
    def __init__(self):
        ...

    def set_category_score(self, category: Category, dice: list[int] | None) -> None:
        """Set score based on category and dice.  If dice is None then zero category."""
        pass

    def get_category_score(self, category: Category) -> int:
        """Get the score associated with a particular category."""
        pass

    def get_score(self) -> int:
        """Get the score across all categories including bonuses."""
        pass