from enum import Enum
from typing import NamedTuple

Section = Enum("Section", ["UPPER", "LOWER"])


class CategoryValue(NamedTuple):
    name: str
    number: int | None
    section: Section


class Category(Enum):
    ACES = CategoryValue("ACES", 1, Section.UPPER)
    TWOS = CategoryValue("TWOS", 2, Section.UPPER)
    THREES = CategoryValue("THREES", 3, Section.UPPER)
    FOURS = CategoryValue("FOURS", 4, Section.UPPER)
    FIVES = CategoryValue("FIVES", 5, Section.UPPER)
    SIXES = CategoryValue("SIXES", 6, Section.UPPER)

    THREE_OF_A_KIND = CategoryValue("THREE_OF_A_KIND", None, Section.LOWER)
    FOUR_OF_A_KIND = CategoryValue("FOUR_OF_A_KIND", None, Section.LOWER)
    FULL_HOUSE = CategoryValue("FULL_HOUSE", None, Section.LOWER)
    SMALL_STRAIGHT = CategoryValue("SMALL_STRAIGHT", None, Section.LOWER)
    LARGE_STRAIGHT = CategoryValue("LARGE_STRAIGHT", None, Section.LOWER)
    YAHTZEE = CategoryValue("YAHTZEE", None, Section.LOWER)
    CHANCE = CategoryValue("CHANCE", None, Section.LOWER)

    @property
    def number(self) -> int | None:
        return self.value.number

    @property
    def section(self) -> Section:
        return self.value.section

    @classmethod
    def get_upper_categories(cls) -> list["Category"]:
        return [c for c in cls if c.section == Section.UPPER]

    @classmethod
    def get_lower_categories(cls) -> list["Category"]:
        return [c for c in cls if c.section == Section.LOWER]

    @classmethod
    def from_number(cls, die: int) -> "Category":
        return {
            1: cls.ACES,
            2: cls.TWOS,
            3: cls.THREES,
            4: cls.FOURS,
            5: cls.FIVES,
            6: cls.SIXES,
        }[die]
