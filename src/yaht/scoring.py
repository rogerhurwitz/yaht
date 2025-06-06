# src/yaht/scoring.py

from yaht.common import UPPER_CATEGORY_TO_DIE, Category, Combo


def score(category: Category, combo: Combo) -> int:
    # We'll rely on the caller to validate playability
    match category:
        case (
            Category.ACES
            | Category.TWOS
            | Category.THREES
            | Category.FOURS
            | Category.FIVES
            | Category.SIXES
        ):
            return _score_upper_category(category, combo)
        case Category.THREE_OF_A_KIND:
            return sum(combo)
        case Category.FOUR_OF_A_KIND:
            return sum(combo)
        case Category.FULL_HOUSE:
            return 25
        case Category.SMALL_STRAIGHT:
            return 30
        case Category.LARGE_STRAIGHT:
            return 40
        case Category.YAHTZEE:
            return 50
        case Category.CHANCE:
            return sum(combo)
        case _:
            raise ValueError(f"Unknown category: {category}")


def _score_upper_category(category: Category, combo: Combo) -> int:
    """Sum only dice values matching category (e.g, Twos: [2, 3, 4, 2, 5] -> 4."""
    target_die = UPPER_CATEGORY_TO_DIE[category]
    return sum(d for d in combo if d == target_die)
