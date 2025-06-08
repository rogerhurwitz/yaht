# src/yaht/validate.py
from collections import Counter
from typing import TYPE_CHECKING, TypeAlias

from yaht.category import Category

# from yaht.dice import DiceList
DiceList: TypeAlias = list[int]

if TYPE_CHECKING:
    from yaht.scorecard import ScorecardLike  # Needed to avoid circular dependency


def is_yahtzee(dice: DiceList) -> bool:
    """Check if all dice have the same value (Yahtzee)."""
    return len(set(dice)) == 1


def is_playable(
    category: Category,
    combo: DiceList,
    card: "ScorecardLike",
    match_zero_playable: bool = False,
) -> bool:
    """True if combo is playable for the specified category/card else False."""

    if not _is_valid_input(category, combo, card):
        return False

    if _joker_rules_active(combo, card):
        return _is_playable_joker_rules(category, combo, card)

    return _is_playable_standard_rules(category, combo, match_zero_playable)


def _joker_rules_active(combo: DiceList, card: "ScorecardLike") -> bool:
    return is_yahtzee(combo) and card.category_scores.get(Category.YAHTZEE) is not None


def _is_valid_input(category: Category, combo: DiceList, card: "ScorecardLike") -> bool:
    return (
        category in Category
        and card.category_scores.get(category) is None
        and len(combo) == 5
        and all(1 <= d <= 6 for d in combo)
    )


def _is_playable_joker_rules(
    category: Category, combo: DiceList, card: "ScorecardLike"
) -> bool:
    # Under joker rules, free upper matching category must be scored first
    matching_upper_category = Category.from_die(combo[0])
    if card.category_scores[matching_upper_category] is None:
        return category == matching_upper_category

    # Okay: upper matching category scored, lower specified category is free
    if category in Category.get_lower_categories():
        return True

    # Okay: upper category specified, no free lower categories to be filled
    no_free_lower_categories = all(
        card.category_scores[c] is not None for c in Category.get_lower_categories()
    )
    if no_free_lower_categories:
        return True

    # Not Okay: upper category specified, but a lower category is free
    return False


def _is_playable_standard_rules(
    category: Category, combo: DiceList, match_zero_playable: bool
) -> bool:
    if match_zero_playable:
        return True  # Shortcut: any unscored category allowed

    counter = Counter(combo)
    sorted_combo = sorted(combo)

    if category in Category.get_upper_categories() or category == Category.CHANCE:
        return True  # Always playable if unscored

    if category == Category.THREE_OF_A_KIND:
        return max(counter.values()) >= 3

    if category == Category.FOUR_OF_A_KIND:
        return max(counter.values()) >= 4

    if category == Category.FULL_HOUSE:
        return sorted(counter.values()) in [[2, 3], [5]]

    if category == Category.SMALL_STRAIGHT:
        straights = [{1, 2, 3, 4}, {2, 3, 4, 5}, {3, 4, 5, 6}]
        return any(set(sorted_combo).issuperset(s) for s in straights)

    if category == Category.LARGE_STRAIGHT:
        return sorted_combo == [1, 2, 3, 4, 5] or sorted_combo == [2, 3, 4, 5, 6]

    if category == Category.YAHTZEE:
        return is_yahtzee(combo)

    return False
