# src/yaht/validate.py
from typing import TYPE_CHECKING

from yaht.category import Category
from yaht.dice import DiceRoll

if TYPE_CHECKING:
    from yaht.scorecard import ScorecardLike  # Needed to avoid circular dependency


def is_playable(
    category: Category,
    roll: DiceRoll,
    card: "ScorecardLike",
    zero_scoring_okay: bool = False,
) -> bool:
    """True if combo is playable for the specified category/card else False."""

    # Cannot score a category that is already scored
    if _is_scored(category, card):
        return False

    if _joker_rules_active(roll, card):
        return _is_playable_joker_rules(category, roll, card)

    return _is_playable_standard_rules(category, roll, zero_scoring_okay)


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
    category: Category, roll: DiceRoll, zero_scoring_okay: bool
) -> bool:
    # Any unscored category is playable when okay to score a category as zero
    if zero_scoring_okay:
        return True

    return category in roll
