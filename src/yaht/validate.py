# src/yaht/validate.py
from collections import Counter  # Standard library, used for counting dice values

from yaht.scorecard import Scorecard
from yaht.utils import DIE_TO_UPPER_CATEGORY, Category, Combo


def is_playable(category: Category, combo: Combo, card: Scorecard) -> bool:
    """True if combo is playable for the specified category/card else False.

    Validates based on Yahtzee rules, including standard category requirements and
    special Joker rules for Yahtzee when the Yahtzee category is already scored.
    """

    # Helper functions for standard category validation (defined locally for independence)
    def has_n_of_a_kind(dice: Combo, n: int) -> bool:
        """Check if there are at least n dice of the same value (for 3/4 of a kind)."""
        if not dice:
            return False
        counts = Counter(dice)
        return any(count >= n for count in counts.values())

    def is_full_house(dice: Combo) -> bool:
        """Check for exactly three of one number and two of another."""
        if not dice:
            return False
        counts = sorted(Counter(dice).values())
        return counts in ([2, 3], [5])

    def has_straight(dice: Combo, length: int) -> bool:
        """Check for a sequence of 'length' consecutive numbers (for small/large straight)."""
        if not dice:
            return False
        unique = sorted(set(dice))
        if len(unique) < length:
            return False
        for i in range(len(unique) - length + 1):
            if unique[i + length - 1] - unique[i] == length - 1:
                return True
        return False

    # Step 1: Check if the category is already scored (rules: each box filled only once)
    if card.scores.get(category) is not None:
        return False

    # Step 2: Validate dice basics (must be exactly 5 dice, each 1-6; rules imply standard dice)
    if len(combo) != 5 or any(d < 1 or d > 6 for d in combo):
        return False

    # Step 3: Check for Yahtzee (5 of a kind) and apply Joker rules if Yahtzee is already scored
    is_yahtzee_combo = len(set(combo)) == 1
    if is_yahtzee_combo and card.scores[Category.YAHTZEE] is not None:
        # Rules: If Yahtzee is scored, must follow Joker rules
        die_value = combo[0]  # All dice are the same
        upper_cat = DIE_TO_UPPER_CATEGORY.get(die_value)
        if upper_cat and card.scores[upper_cat] is None:
            # Rules: Must score in the corresponding Upper Section if open
            return category == upper_cat
        else:
            # Rules: If Upper is filled, allow any open Lower Section category (Joker allows forced scoring)
            lower_categories = {
                Category.THREE_OF_A_KIND,
                Category.FOUR_OF_A_KIND,
                Category.FULL_HOUSE,
                Category.SMALL_STRAIGHT,
                Category.LARGE_STRAIGHT,
                Category.CHANCE,
            }
            return category in lower_categories

    # Step 4: Standard validation for non-Joker cases (based on rules for each category)
    # Upper Section: Always playable (score sum of matching dice, even if 0)
    upper_categories = {
        Category.ACES,
        Category.TWOS,
        Category.THREES,
        Category.FOURS,
        Category.FIVES,
        Category.SIXES,
    }
    if category in upper_categories:
        return True
    elif category == Category.THREE_OF_A_KIND:
        # Rules: Requires 3 or more of the same number
        return has_n_of_a_kind(combo, 3)
    elif category == Category.FOUR_OF_A_KIND:
        # Rules: Requires 4 or more of the same number
        return has_n_of_a_kind(combo, 4)
    elif category == Category.FULL_HOUSE:
        # Rules: Requires three of one number and two of another
        return is_full_house(combo)
    elif category == Category.SMALL_STRAIGHT:
        # Rules: Requires sequence of 4 consecutive numbers
        return has_straight(combo, 4)
    elif category == Category.LARGE_STRAIGHT:
        # Rules: Requires sequence of 5 consecutive numbers
        return has_straight(combo, 5)
    elif category == Category.YAHTZEE:
        # Rules: Requires all 5 dice the same
        return is_yahtzee_combo
    elif category == Category.CHANCE:
        # Rules: Always playable (any 5 dice)
        return True
    else:
        # Unknown category
        return False
