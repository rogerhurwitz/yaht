# src/yaht/player.py
from collections import Counter
from typing import Dict, List, Protocol, Tuple

from yaht.category import Category
from yaht.dice import Dice
from yaht.playable import is_playable, is_yahtzee
from yaht.scorecard import ScorecardView


class Player(Protocol):
    def take_turn(self, dice: Dice, view: ScorecardView) -> Category:
        """
        Given a Dice object and a read-only view of the scorecard, decide on a
        scoring category. The GameManager will handle actual scoring and rule
        enforcement.
        """


class TestPlayer:
    def take_turn(self, dice: Dice, view: ScorecardView) -> Category:
        """
        Optimizes dice rolls and selects the highest scoring category.
        Takes into account upper section and Yahtzee bonus rules.
        """
        # First roll is already done by the Dice class initialization

        # Second roll
        if dice.roll_count < 2:
            self._optimize_roll(dice, view)

        # Third roll
        if dice.roll_count < 3:
            self._optimize_roll(dice, view)

        # Choose the best category based on current dice values
        return self._select_best_category(dice.values, view)

    def _optimize_roll(self, dice: Dice, view: ScorecardView) -> None:
        """Decides which dice to keep and which to reroll."""
        current_values = dice.values
        counter = Counter(current_values)

        # Check if we already have a Yahtzee
        if max(counter.values()) == 5 and Category.YAHTZEE in view.get_unscored_categories():
            # Already have a Yahtzee, keep all dice
            return

        # Check if we already have a Large Straight
        if (
            sorted(current_values) in [[1, 2, 3, 4, 5], [2, 3, 4, 5, 6]]
            and Category.LARGE_STRAIGHT in view.get_unscored_categories()
        ):
            # Already have a Large Straight, keep all dice
            return

        # Check if we already have a Full House
        if (
            sorted(counter.values()) == [2, 3]
            and Category.FULL_HOUSE in view.get_unscored_categories()
        ):
            # Already have a Full House, keep all dice
            return

        # Check if we have 4 of a kind
        if max(counter.values()) >= 4:
            # Keep the 4 matching dice, reroll the other
            most_common = counter.most_common(1)[0][0]
            reroll_indices = [i for i, val in enumerate(current_values) if val != most_common]
            if len(reroll_indices) > 1:  # Only keep 4 if we have more than 4
                reroll_indices = reroll_indices[:1]
            if reroll_indices:  # Only reroll if we have dice to reroll
                dice.reroll(reroll_indices)
            return

        # Check for potential small straight
        unique_values = set(current_values)
        if len(unique_values) >= 4:
            # Check if we have a sequence of 4
            for straight in [{1, 2, 3, 4}, {2, 3, 4, 5}, {3, 4, 5, 6}]:
                if (
                    straight.issubset(unique_values)
                    and Category.SMALL_STRAIGHT in view.get_unscored_categories()
                ):
                    # We have a small straight, reroll the non-straight die to try for large straight
                    non_straight_indices = [
                        i for i, val in enumerate(current_values) if val not in straight
                    ]
                    if non_straight_indices:
                        dice.reroll(non_straight_indices)
                    return

            # Check for potential large straight (4 out of 5 consecutive numbers)
            for straight in [{1, 2, 3, 4, 5}, {2, 3, 4, 5, 6}]:
                if len(straight.intersection(unique_values)) >= 4:
                    # We have 4 out of 5 for a large straight, reroll the non-straight dice
                    reroll_indices = [
                        i for i, val in enumerate(current_values) if val not in straight
                    ]
                    if reroll_indices:
                        dice.reroll(reroll_indices)
                    return

        # Check for 3 of a kind
        if max(counter.values()) >= 3:
            most_common = counter.most_common(1)[0][0]
            # Keep the 3 matching dice, reroll the others
            reroll_indices = [i for i, val in enumerate(current_values) if val != most_common]
            if reroll_indices:
                dice.reroll(reroll_indices)
            return

        # Check for pairs
        pairs = [val for val, count in counter.items() if count >= 2]
        if pairs:
            # If we have a pair, keep the highest pair and reroll the rest
            highest_pair = max(pairs)
            reroll_indices = [i for i, val in enumerate(current_values) if val != highest_pair]
            if reroll_indices:
                dice.reroll(reroll_indices)
            return

        # If no clear strategy, prioritize high-value dice (5s and 6s)
        high_values = [5, 6]
        reroll_indices = [i for i, val in enumerate(current_values) if val not in high_values]
        if reroll_indices:
            dice.reroll(reroll_indices)
            return

        # If all else fails, reroll all dice
        dice.reroll([0, 1, 2, 3, 4])

    def _select_best_category(self, dice_values: List[int], view: ScorecardView) -> Category:
        """Selects the best category based on current dice values and scorecard state."""
        unscored_categories = view.get_unscored_categories()

        # Calculate potential scores for each unscored category
        category_scores: Dict[Category, int] = {}
        for category in unscored_categories:
            if is_playable(category, dice_values, view):
                category_scores[category] = self._calculate_score(category, dice_values)

        # Check for Yahtzee bonus opportunity
        if is_yahtzee(dice_values) and view.category_scores.get(Category.YAHTZEE) == 50:
            # With a Yahtzee bonus, we must follow Joker rules
            # First, try to score in the corresponding Upper Section box
            try:
                upper_match = Category.from_die(dice_values[0])
                if upper_match in unscored_categories:
                    return upper_match
            except KeyError:
                pass

        # Consider upper section bonus
        upper_categories = Category.get_upper_categories()
        upper_score = sum(view.category_scores.get(cat, 0) or 0 for cat in upper_categories)
        remaining_upper = [cat for cat in upper_categories if cat in unscored_categories]

        # If we're close to the upper bonus and have upper categories left, prioritize them
        if upper_score < 63 and len(remaining_upper) > 0:
            needed_for_bonus = 63 - upper_score
            # If we can get the bonus with remaining categories, prioritize upper section
            if self._can_achieve_upper_bonus(
                remaining_upper, needed_for_bonus, dice_values, category_scores
            ):
                # Find the best upper category
                best_upper = max(
                    (cat for cat in remaining_upper if cat in category_scores),
                    key=lambda cat: category_scores.get(cat, 0),
                    default=None,
                )
                if best_upper:
                    return best_upper

        # If no special cases apply, choose the highest scoring category
        if category_scores:
            return max(category_scores.items(), key=lambda x: x[1])[0]

        # If no playable categories (shouldn't happen), zero out the least valuable category
        return min(unscored_categories, key=lambda cat: self._get_category_potential(cat))

    def _calculate_score(self, category: Category, dice_values: List[int]) -> int:
        """Calculate the score for a given category and dice combination."""
        counter = Counter(dice_values)

        # Upper section scoring
        if category in Category.get_upper_categories():
            try:
                die_value = category.die_value
                return die_value * counter[die_value]
            except KeyError:
                return 0

        # Lower section scoring
        if category == Category.THREE_OF_A_KIND:
            if max(counter.values()) >= 3:
                return sum(dice_values)
            return 0

        elif category == Category.FOUR_OF_A_KIND:
            if max(counter.values()) >= 4:
                return sum(dice_values)
            return 0

        elif category == Category.FULL_HOUSE:
            if sorted(counter.values()) == [2, 3] or max(counter.values()) == 5:
                return 25
            return 0

        elif category == Category.SMALL_STRAIGHT:
            straights = [{1, 2, 3, 4}, {2, 3, 4, 5}, {3, 4, 5, 6}]
            if any(straight.issubset(set(dice_values)) for straight in straights):
                return 30
            return 0

        elif category == Category.LARGE_STRAIGHT:
            if sorted(dice_values) in [[1, 2, 3, 4, 5], [2, 3, 4, 5, 6]]:
                return 40
            return 0

        elif category == Category.YAHTZEE:
            if len(set(dice_values)) == 1:
                return 50
            return 0

        elif category == Category.CHANCE:
            return sum(dice_values)

        return 0

    def _can_achieve_upper_bonus(
        self,
        remaining_upper: List[Category],
        needed_points: int,
        dice_values: List[int],
        category_scores: Dict[Category, int],
    ) -> bool:
        """Check if we can still achieve the upper section bonus."""
        # Calculate maximum potential from remaining categories
        potential = 0
        for cat in remaining_upper:
            die_value = cat.die_value
            potential += die_value * 5  # Maximum possible (5 of that number)

        # If current dice give enough points, prioritize upper section
        current_upper_potential = sum(category_scores.get(cat, 0) for cat in remaining_upper)

        return potential >= needed_points or current_upper_potential >= needed_points

    def _get_category_potential(self, category: Category) -> int:
        """Returns the maximum potential score for a category."""
        if category in Category.get_upper_categories():
            try:
                die_value = category.die_value
                return die_value * 5  # Maximum is 5 dice of this value
            except KeyError:
                return 0
        elif category == Category.THREE_OF_A_KIND:
            return 30  # Approximate max (5 sixes)
        elif category == Category.FOUR_OF_A_KIND:
            return 30  # Approximate max (5 sixes)
        elif category == Category.FULL_HOUSE:
            return 25
        elif category == Category.SMALL_STRAIGHT:
            return 30
        elif category == Category.LARGE_STRAIGHT:
            return 40
        elif category == Category.YAHTZEE:
            return 50
        elif category == Category.CHANCE:
            return 30  # Approximate max (5 sixes)
        return 0
