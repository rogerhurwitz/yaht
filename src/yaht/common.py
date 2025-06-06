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


UPPER_SECTION_CATEGORIES = [
    Category.ACES,
    Category.TWOS,
    Category.THREES,
    Category.FOURS,
    Category.FIVES,
    Category.SIXES,
]

LOWER_SECTION_CATEGORIES = [
    Category.THREE_OF_A_KIND,
    Category.FOUR_OF_A_KIND,
    Category.FULL_HOUSE,
    Category.SMALL_STRAIGHT,
    Category.LARGE_STRAIGHT,
    Category.YAHTZEE,
    Category.CHANCE,
]

DIE_TO_UPPER_CATEGORY = {
    1: Category.ACES,
    2: Category.TWOS,
    3: Category.THREES,
    4: Category.FOURS,
    5: Category.FIVES,
    6: Category.SIXES,
}

UPPER_CATEGORY_TO_DIE = {v: k for k, v in DIE_TO_UPPER_CATEGORY.items()}

Combo = list[int]


def is_yahtzee(combo: Combo) -> bool:
    """True if combo is a Yahtzee else False."""
    return len(set(combo)) == 1
