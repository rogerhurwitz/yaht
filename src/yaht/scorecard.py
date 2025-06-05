# src/yaht/scorecard.py
from yaht.exceptions import (
    CategoryAlreadyScored,
    DiceCountError,
    DieValueError,
    InvalidCategoryError,
)
from yaht.scoring import score
from yaht.utils import DIE_TO_UPPER_CATEGORY, Category

UPPER_BONUS_SCORE = 35
UPPER_BONUS_THRESHOLD = 63
YAHTZEE_BONUS_SCORE = 100


UPPER_CATEGORY_TO_DIE = {v: k for k, v in DIE_TO_UPPER_CATEGORY.items()}


class Scorecard:
    """Tracks the score for a single player."""

    @staticmethod
    def is_yahtzee(dice: list[int]) -> bool:
        """Check if all dice have the same value (Yahtzee)."""
        return len(set(dice)) == 1

    def __init__(self):
        # Initialize all categories to None (not scored yet)
        self.scores: dict[Category, int | None] = {category: None for category in Category}
        self.yahtzee_bonus_count = 0

    def zero_category(self, category: Category) -> None:
        if self.scores[category] is not None:
            raise CategoryAlreadyScored(f"Category {category.name} has already been scored")
        self.scores[category] = 0

    def set_category_score(self, category: Category, dice: list[int]) -> None:
        """Set score for specified category based on dice values."""

        #  --- Check for Input Errors  ---

        if category not in self.scores:
            raise InvalidCategoryError(f"Unknown category: {category}")

        if self.scores[category] is not None:
            raise CategoryAlreadyScored(f"Category {category.name} has already been scored")

        self._raise_on_invalid_dice(dice)

        # --- Apply Joker Rules ---

        if self.is_yahtzee(dice) and self.scores[Category.YAHTZEE] is not None:
            upper_category = DIE_TO_UPPER_CATEGORY[dice[0]]
            if self.scores[upper_category] is None and category != upper_category:
                raise InvalidCategoryError(
                    f"Must score Yahtzee in {upper_category.name} before choosing another category."
                )

        # --- Begin Scoring Dice ---

        # call the appropriate scorer
        self.scores[category] = score(category, dice)

        # Handle Yahtzee bonus
        if (
            self.is_yahtzee(dice)
            and category != Category.YAHTZEE
            and self.scores[Category.YAHTZEE] == 50
        ):
            self.yahtzee_bonus_count += 1

    def get_category_score(self, category: Category) -> int:
        """Get the score associated with a particular category."""
        if category not in self.scores:
            raise InvalidCategoryError(f"Unknown category: {category}")

        score = self.scores[category]
        return score if score is not None else 0

    def get_score(self) -> int:
        """Get the score across all categories including bonuses."""
        # Calculate upper section score
        upper_section = [
            Category.ACES,
            Category.TWOS,
            Category.THREES,
            Category.FOURS,
            Category.FIVES,
            Category.SIXES,
        ]
        upper_score = sum(self.get_category_score(cat) for cat in upper_section)

        # Add upper section bonus if applicable
        upper_bonus = UPPER_BONUS_SCORE if upper_score >= UPPER_BONUS_THRESHOLD else 0

        # Calculate lower section score
        lower_section = [
            Category.THREE_OF_A_KIND,
            Category.FOUR_OF_A_KIND,
            Category.FULL_HOUSE,
            Category.SMALL_STRAIGHT,
            Category.LARGE_STRAIGHT,
            Category.YAHTZEE,
            Category.CHANCE,
        ]
        lower_score = sum(self.get_category_score(cat) for cat in lower_section)

        # Add Yahtzee bonus
        yahtzee_bonus = self.yahtzee_bonus_count * YAHTZEE_BONUS_SCORE

        # Return total score
        return upper_score + upper_bonus + lower_score + yahtzee_bonus

    def _raise_on_invalid_dice(self, dice: list[int]) -> None:
        if len(dice) != 5:
            raise DiceCountError(f"Invalid dice count: {len(dice)}")
        if any(d < 1 or d > 6 for d in dice):
            raise DieValueError("The value of all dice must be between 1 and 6.")

    def __str__(self) -> str:
        scored = {cat.name: score for cat, score in self.scores.items() if score is not None}
        return f"Scorecard({scored}, bonuses={self.yahtzee_bonus_count})"
