# src/yaht/validate.py
from collections import Counter

from yaht.common import DIE_TO_UPPER_CATEGORY, Category, Combo, is_yahtzee
from yaht.scorecard import Scorecard


def is_playable(category: Category, combo: Combo, card: Scorecard) -> bool:
    """True if combo is playable for the specified category/card else False.

    Validates based on Yahtzee rules, including standard category requirements
    and special Joker rules for additional Yahtzees.
    """
    # Check if the category is already scored (not playable if it is)
    if card.scores.get(category) is not None:
        return False

    # Validate dice count and values (aligns with Scorecard._raise_on_invalid_dice)
    if len(combo) != 5 or any(d < 1 or d > 6 for d in combo):
        return False

    # Check for Yahtzee and apply Joker rules if Yahtzee is already scored
    yahtzee_scored = card.scores[Category.YAHTZEE] is not None
    if is_yahtzee(combo) and yahtzee_scored:
        # Determine the corresponding Upper Section category for this Yahtzee
        upper_match = DIE_TO_UPPER_CATEGORY.get(combo[0])
        if upper_match and card.scores[upper_match] is None:
            # Per rules and Scorecard logic, must choose the available Upper Section category
            return category == upper_match
        else:
            # If Upper Section match is unavailable, can choose any open Lower Section category
            # (Joker rules allow scoring regardless of usual requirements)
            lower_categories = [
                Category.THREE_OF_A_KIND,
                Category.FOUR_OF_A_KIND,
                Category.FULL_HOUSE,
                Category.SMALL_STRAIGHT,
                Category.LARGE_STRAIGHT,
                Category.CHANCE,
            ]
            if category in lower_categories:
                return True
            # Cannot choose other Upper Section categories or Yahtzee again
            return False

    # Standard validation for non-Joker cases
    combo_counter = Counter(combo)
    sorted_combo = sorted(combo)

    # --- Upper Section Validation ---

    if category in [
        Category.ACES,
        Category.TWOS,
        Category.THREES,
        Category.FOURS,
        Category.FIVES,
        Category.SIXES,
    ]:
        # U-S category is always playable if unplayed (score will be 0 if no die match)
        return True

    # ___ Lower Section Validation ---

    elif category == Category.THREE_OF_A_KIND:
        # Requires at least 3 of the same number
        return max(combo_counter.values()) >= 3

    elif category == Category.FOUR_OF_A_KIND:
        # Requires at least 4 of the same number
        return max(combo_counter.values()) >= 4

    elif category == Category.FULL_HOUSE:
        # Requires 3 of a kind and 2 of a kind (can be satisifed by 5 of a kind)
        return sorted(combo_counter.values()) in [[2, 3], [5]]

    elif category == Category.SMALL_STRAIGHT:
        # Requires a sequence of at least 4 consecutive numbers
        straights = [{1, 2, 3, 4}, {2, 3, 4, 5}, {3, 4, 5, 6}]
        return any(set(sorted_combo).issuperset(s) for s in straights)

    elif category == Category.LARGE_STRAIGHT:
        # Requires exactly 1-2-3-4-5 or 2-3-4-5-6
        return sorted_combo == [1, 2, 3, 4, 5] or sorted_combo == [2, 3, 4, 5, 6]

    elif category == Category.YAHTZEE:
        # Requires all 5 dice the same
        return is_yahtzee(combo)

    elif category == Category.CHANCE:
        # Always playable if unplayed
        return True

    # Default for invalid/unknown categories
    return False
