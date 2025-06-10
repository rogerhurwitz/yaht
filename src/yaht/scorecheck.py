# src/yaht/validate.py
from typing import TYPE_CHECKING

from yaht.category import Category, Section
from yaht.diceroll import DiceRoll
from yaht.exceptions import InvalidCategoryError

if TYPE_CHECKING:
    from yaht.scorecard import ScorecardLike  # Needed to avoid circular dependency


def calculate_combo_score(category: Category, roll: DiceRoll) -> int:
    """Determine value of combination based on absolute or relative score."""
    if category.section == Section.UPPER:
        return _calculate_upper_score(category, roll)
    elif category is Category.FULL_HOUSE:
        return 25
    elif category is Category.SMALL_STRAIGHT:
        return 30
    elif category is Category.LARGE_STRAIGHT:
        return 40
    elif category is Category.YAHTZEE:
        return 50
    elif category in [Category.THREE_OF_A_KIND, Category.FOUR_OF_A_KIND, Category.CHANCE]:
        return sum(roll)
    else:
        raise InvalidCategoryError(f"Unknown category: {category}")


def _calculate_upper_score(category: Category, roll: DiceRoll) -> int:
    """Sum only dice values matching category (e.g, Twos: [2, 3, 4, 2, 5] -> 4."""
    target_number = category.die_number
    return sum(n for n in roll if n == target_number)


def is_combo_scoreable(
    category: Category,
    roll: DiceRoll,
    card: "ScorecardLike",
    zero_scoreable: bool = False,
) -> bool:
    """True if combo is playable for the specified category/card else False."""

    # Cannot score a category that is already scored
    if _is_scored(category, card):
        return False

    if Category.YAHTZEE in roll and _joker_rules_active(roll, card):
        return _is_scoreable_joker_rules(category, roll, card)

    return _is_scoreable_standard_rules(category, roll, zero_scoreable)


def _is_scored(category: Category, card: "ScorecardLike") -> bool:
    """Checks to see if card category is already scored."""
    return card.category_scores[category] is not None


def _joker_rules_active(roll: DiceRoll, card: "ScorecardLike") -> bool:
    return _is_scored(Category.YAHTZEE, card)


def _is_scoreable_joker_rules(
    category: Category, roll: DiceRoll, card: "ScorecardLike"
) -> bool:
    # Under joker rules, free upper matching category must be scored first
    matched_category = Category.from_number(roll[0])
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


def _is_scoreable_standard_rules(
    category: Category, roll: DiceRoll, zero_scoreable: bool
) -> bool:
    # Any category is scoreable when okay to assign zero as score
    if zero_scoreable:
        return True
    # Otherwise, roll combination requirements (if any) must be met
    return category in roll
