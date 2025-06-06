# src/yaht/scoring.py

from yaht.common import UPPER_CATEGORY_TO_DIE, Category


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
    # No upper category combination requirements - scores zero if no target matches
    target = UPPER_CATEGORY_TO_DIE[category]
    return sum(d for d in dice if d == target)


def _score_three_of_a_kind(dice: list[int]) -> int:
    """Sum all 5 dice (assumes validation handled by is_playable)."""
    return sum(dice)  # Removed validation and error-raising


def _score_four_of_a_kind(dice: list[int]) -> int:
    """Sum all 5 dice (assumes validation handled by is_playable)."""
    return sum(dice)  # Removed validation and error-raising


def _score_full_house(dice: list[int]) -> int:
    """Score 25 points (assumes validation handled by is_playable)."""
    return 25  # Removed validation and error-raising


def _score_small_straight(dice: list[int]) -> int:
    """Score 30 points (assumes validation handled by is_playable)."""
    return 30  # Removed validation and error-raising


def _score_large_straight(dice: list[int]) -> int:
    """Score 40 points (assumes validation handled by is_playable)."""
    return 40  # Removed validation and error-raising


def _score_yahtzee(dice: list[int]) -> int:
    """Score 50 points (assumes validation handled by is_playable)."""
    return 50  # Removed validation and error-raising
