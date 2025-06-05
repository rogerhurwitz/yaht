# src/yaht/scoring.py
from collections import Counter

from yaht.utils import UPPER_CATEGORY_TO_DIE, Category, is_yahtzee


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
    """Sum only dice values matching category (e.g, Twos: [2, 3, 4, 2, 5] -> 4."""
    target = UPPER_CATEGORY_TO_DIE[category]
    return sum(d for d in dice if d == target)


def _score_three_of_a_kind(dice: list[int]) -> int:
    """Sum all 5 dice (not just 3 of a kind (e.g., [3, 3, 3, 4, 5] -> 18."""
    counts = Counter(dice)
    return sum(dice) if any(c >= 3 for c in counts.values()) else 0


def _score_four_of_a_kind(dice: list[int]) -> int:
    """Sum all 5 dice (not just 4 of a kind (e.g., [3, 3, 3, 3, 5] -> 17."""
    counts = Counter(dice)
    return sum(dice) if any(c >= 4 for c in counts.values()) else 0


def _score_full_house(dice: list[int]) -> int:
    """Score 25 points for patterns (3 pair + 2 pair) matching full house."""
    counts = sorted(Counter(dice).values(), reverse=True)
    return 25 if counts in ([5], [3, 2]) else 0  # [5] is Yahtzee


def _score_small_straight(dice: list[int]) -> int:
    """Score 30 points for 4 dice run (or Yahtzee)."""
    unique = set(dice)
    straights = [{1, 2, 3, 4}, {2, 3, 4, 5}, {3, 4, 5, 6}]
    if any(s.issubset(unique) for s in straights) or is_yahtzee(dice):
        return 30
    return 0


def _score_large_straight(dice: list[int]) -> int:
    """Score 40 points for 5 dice run (or Yahtzee)."""
    if set(dice) in ({1, 2, 3, 4, 5}, {2, 3, 4, 5, 6}) or is_yahtzee(dice):
        return 40
    return 0


def _score_yahtzee(dice: list[int]) -> int:
    """Score 50 points for a Yahtzee"""
    return 50 if is_yahtzee(dice) else 0
