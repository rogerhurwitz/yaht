# src/yaht/validate.py
from typing import TYPE_CHECKING

from yaht.category import Category
from yaht.dice import DiceRoll

if TYPE_CHECKING:
    from yaht.scorecard import ScorecardLike  # Needed to avoid circular dependency


def calculate_score(category: Category, roll: DiceRoll) -> int:
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
            return _calculate_upper_category_score(category, roll)
        case Category.THREE_OF_A_KIND:
            return sum(roll)
        case Category.FOUR_OF_A_KIND:
            return sum(roll)
        case Category.FULL_HOUSE:
            return 25
        case Category.SMALL_STRAIGHT:
            return 30
        case Category.LARGE_STRAIGHT:
            return 40
        case Category.YAHTZEE:
            return 50
        case Category.CHANCE:
            return sum(roll)
        case _:
            raise ValueError(f"Unknown category: {category}")


def _calculate_upper_category_score(category: Category, roll: DiceRoll) -> int:
    """Sum only dice values matching category (e.g, Twos: [2, 3, 4, 2, 5] -> 4."""
    target_die = category.die_value
    return sum(d for d in roll if d == target_die)


def is_scoreable(
    category: Category,
    roll: DiceRoll,
    card: "ScorecardLike",
    zero_scoreable: bool = False,
) -> bool:
    """True if combo is playable for the specified category/card else False."""

    # Cannot score a category that is already scored
    if _is_scored(category, card):
        return False

    if _joker_rules_active(roll, card):
        return _is_playable_joker_rules(category, roll, card)

    return _is_playable_standard_rules(category, roll, zero_scoreable)


def _is_scored(category: Category, card: "ScorecardLike") -> bool:
    """Checks to see if card category is already scored."""
    return card.category_scores[category] is not None


def _joker_rules_active(roll: DiceRoll, card: "ScorecardLike") -> bool:
    return _is_scored(Category.YAHTZEE, card)


def _is_playable_joker_rules(
    category: Category, roll: DiceRoll, card: "ScorecardLike"
) -> bool:
    # Under joker rules, free upper matching category must be scored first
    matched_category = Category.from_die(roll[0])
    if not _is_scored(matched_category, card):
        return category == matched_category

    # If upper matching category is scored then any lower category is playable
    if category in Category.get_lower_categories():
        return True

    # Can only play a non-matching upper category if all lower categories scored
    no_free_lower_categories = all(
        _is_scored(c, card) for c in Category.get_lower_categories()
    )
    return True if no_free_lower_categories else False


def _is_playable_standard_rules(
    category: Category, roll: DiceRoll, zero_scoreable: bool
) -> bool:
    # Any unscored category is playable when okay to score a category as zero
    if zero_scoreable:
        return True
    # Otherwise, roll combination requirements (if any) must be met
    return category in roll
