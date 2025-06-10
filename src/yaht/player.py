# src/yaht/player.py
from collections import Counter
from typing import Protocol

from yaht.category import Category
from yaht.dicetypes import DiceRoll
from yaht.game import PlayerGameState
from yaht.scorecard import ScorecardView
from yaht.scorecheck import calculate_combo_score, is_combo_scoreable


class Player(Protocol):
    name: str

    def take_turn(self, state: PlayerGameState) -> Category:
        """Roll dice then choose category to score against."""
        raise NotImplementedError()


class BasicBotPlayer:
    def __init__(self, name: str = "BasicBot"):
        self.name = name

    def take_turn(self, state: PlayerGameState) -> Category:
        """Roll dice then choose category to score against."""
        # Roll dice up to 3 times with simple strategy
        dice_cup = state.dice_cup
        card = state.card

        # First roll - always roll all dice
        roll = dice_cup.roll_dice()

        # Simple reroll strategy for rolls 2 and 3
        for _ in range(2):  # Up to 2 more rolls
            counts = Counter(roll.numbers)
            max_count = max(counts.values())

            # If we have 4+ of a kind, keep them and reroll the rest
            if max_count >= 4:
                most_common_value = counts.most_common(1)[0][0]
                indices_to_reroll = [
                    i for i, val in enumerate(roll.numbers) if val != most_common_value
                ]
                if indices_to_reroll:
                    roll = dice_cup.roll_dice(indices_to_reroll)
                break

            # If we have 3 of a kind, try for Yahtzee if upper section available
            elif max_count == 3:
                most_common_value = counts.most_common(1)[0][0]
                upper_category = Category.from_number(most_common_value)
                if card.category_scores.get(upper_category) is None:
                    # Keep the three and reroll the rest
                    indices_to_reroll = [
                        i for i, val in enumerate(roll.numbers) if val != most_common_value
                    ]
                    if indices_to_reroll:
                        roll = dice_cup.roll_dice(indices_to_reroll)
                    continue

            # If we have a pair of 4s, 5s, or 6s, keep them
            elif max_count == 2:
                most_common_value = counts.most_common(1)[0][0]
                if most_common_value >= 4:
                    indices_to_reroll = [
                        i for i, val in enumerate(roll.numbers) if val != most_common_value
                    ]
                    if indices_to_reroll:
                        roll = dice_cup.roll_dice(indices_to_reroll)
                    continue

            # Otherwise, keep highest values and reroll lowest
            sorted_dice = sorted(roll.numbers, reverse=True)
            if sorted_dice[0] >= 4:  # Keep high values
                indices_to_reroll = [i for i, val in enumerate(roll.numbers) if val < 4]
                if indices_to_reroll:
                    roll = dice_cup.roll_dice(indices_to_reroll)
            else:
                break  # Don't reroll if we don't have a clear strategy

        # Choose category based on strategy
        return self._choose_category(roll, card)

    def _choose_category(self, roll: DiceRoll, card: ScorecardView) -> Category:
        """Choose the best category for the given roll and card state."""
        counts = Counter(roll.numbers)
        max_count = max(counts.values())
        unscored = card.get_unscored_categories()

        # Strategy 1: If we have 4+ of a kind with 4s, 5s, or 6s, use upper section first
        if max_count >= 4:
            most_common_value = counts.most_common(1)[0][0]
            if most_common_value >= 4:
                upper_category = Category.from_number(most_common_value)
                if upper_category in unscored and is_combo_scoreable(
                    upper_category, roll, card
                ):
                    return upper_category

        # Strategy 2: Take Yahtzee if available
        if Category.YAHTZEE in unscored and is_combo_scoreable(Category.YAHTZEE, roll, card):
            return Category.YAHTZEE

        # Strategy 3: Take high-value combinations
        high_value_categories = [
            Category.LARGE_STRAIGHT,
            Category.SMALL_STRAIGHT,
            Category.FULL_HOUSE,
        ]

        for category in high_value_categories:
            if category in unscored and is_combo_scoreable(category, roll, card):
                return category

        # Strategy 4: Fill upper section with good scores (aim for 63+ total)
        upper_scores = []
        for category in Category.get_upper_categories():
            if category in unscored and is_combo_scoreable(category, roll, card):
                score = calculate_combo_score(category, roll)
                die_number = category.die_number
                if (
                    die_number is not None and score >= die_number * 3
                ):  # At least 3 of that number
                    upper_scores.append((category, score))

        if upper_scores:
            # Take the highest scoring upper category
            return max(upper_scores, key=lambda x: x[1])[0]

        # Strategy 5: Take 4 of a kind or 3 of a kind if good score
        if max_count >= 4 and Category.FOUR_OF_A_KIND in unscored:
            if is_combo_scoreable(Category.FOUR_OF_A_KIND, roll, card):
                return Category.FOUR_OF_A_KIND

        if max_count >= 3 and Category.THREE_OF_A_KIND in unscored:
            if (
                is_combo_scoreable(Category.THREE_OF_A_KIND, roll, card)
                and sum(roll.numbers) >= 15
            ):
                return Category.THREE_OF_A_KIND

        # Strategy 6: Use chance as fallback only if it's a decent score
        if Category.CHANCE in unscored and sum(roll.numbers) >= 20:
            return Category.CHANCE

        # Strategy 7: Fill in zeros strategically - prefer 1s, 2s, 3s for zeros
        zero_preference = [Category.ACES, Category.TWOS, Category.THREES, Category.YAHTZEE]
        for category in zero_preference:
            if category in unscored:
                return category

        # Fallback: take any available category
        if unscored:
            return unscored[0]

        # Should never reach here in a proper game
        return Category.CHANCE
