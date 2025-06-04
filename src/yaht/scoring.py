# src/yaht/scoring.py
from collections import Counter

from yaht.constants import UPPER_CATEGORY_TO_DIE, Category


def score(category: Category, dice: list[int]) -> int:
    match category:
        case (
            Category.ACES
            | Category.TWOS
            | Category.THREES
            | Category.FOURS
            | Category.FIVES
            | Category.SIXES
        ):
            return _score_upper_category(category, dice)
        case Category.THREE_OF_A_KIND:
            return _score_three_of_a_kind(dice)
        case Category.FOUR_OF_A_KIND:
            return _score_four_of_a_kind(dice)
        case Category.FULL_HOUSE:
            return _score_full_house(dice)
        case Category.SMALL_STRAIGHT:
            return _score_small_straight(dice)
        case Category.LARGE_STRAIGHT:
            return _score_large_straight(dice)
        case Category.YAHTZEE:
            return _score_yahtzee(dice)
        case Category.CHANCE:
            return sum(dice)
        case _:
            raise ValueError(f"Unknown category: {category}")


def _score_upper_category(category: Category, dice: list[int]) -> int:
    target = UPPER_CATEGORY_TO_DIE[category]
    return sum(d for d in dice if d == target)


def _score_three_of_a_kind(dice: list[int]) -> int:
    counts = Counter(dice)
    return sum(dice) if any(c >= 3 for c in counts.values()) else 0


def _score_four_of_a_kind(dice: list[int]) -> int:
    counts = Counter(dice)
    return sum(dice) if any(c >= 4 for c in counts.values()) else 0


def _score_full_house(dice: list[int]) -> int:
    counts = sorted(Counter(dice).values(), reverse=True)
    return 25 if counts in ([5], [3, 2]) else 0


def _score_small_straight(dice: list[int]) -> int:
    unique = set(dice)
    straights = [{1, 2, 3, 4}, {2, 3, 4, 5}, {3, 4, 5, 6}]
    return 30 if any(s.issubset(unique) for s in straights) else 0


def _score_large_straight(dice: list[int]) -> int:
    return 40 if set(dice) in ({1, 2, 3, 4, 5}, {2, 3, 4, 5, 6}) else 0


def _score_yahtzee(dice: list[int]) -> int:
    return 50 if len(set(dice)) == 1 else 0
