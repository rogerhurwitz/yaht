from enum import Enum


class Section(Enum):
    UPPER = "upper"
    LOWER = "lower"


class Category(Enum):
    ACES = (1, Section.UPPER)
    TWOS = (2, Section.UPPER)
    THREES = (3, Section.UPPER)
    FOURS = (4, Section.UPPER)
    FIVES = (5, Section.UPPER)
    SIXES = (6, Section.UPPER)
    THREE_OF_A_KIND = (None, Section.LOWER)
    FOUR_OF_A_KIND = (None, Section.LOWER)
    FULL_HOUSE = (None, Section.LOWER)
    SMALL_STRAIGHT = (None, Section.LOWER)
    LARGE_STRAIGHT = (None, Section.LOWER)
    YAHTZEE = (None, Section.LOWER)
    CHANCE = (None, Section.LOWER)

    def __init__(self, die_value: int | None, section: Section):
        self._die_value = die_value
        self._section = section

    @property
    def section(self) -> Section:
        return self._section

    @property
    def die_value(self) -> int | None:
        return self._die_value

    @classmethod
    def upper_categories(cls) -> list["Category"]:
        return [c for c in cls if c.section == Section.UPPER]

    @classmethod
    def lower_categories(cls) -> list["Category"]:
        return [c for c in cls if c.section == Section.LOWER]

    @classmethod
    def from_die(cls, die: int) -> "Category":
        return {
            1: cls.ACES,
            2: cls.TWOS,
            3: cls.THREES,
            4: cls.FOURS,
            5: cls.FIVES,
            6: cls.SIXES,
        }[die]
