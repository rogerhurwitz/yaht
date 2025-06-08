# src/yaht/scorecard.py

from typing import Callable, Protocol, cast

from yaht.category import Category
from yaht.exceptions import (
    CategoryAlreadyScored,
    DiceCountError,
    DieValueError,
    InvalidCategoryError,
)
from yaht.playable import is_playable, is_yahtzee
from yaht.scoring import score

UPPER_BONUS_SCORE = 35
UPPER_BONUS_THRESHOLD = 63
YAHTZEE_BONUS_SCORE = 100


class ScorecardLike(Protocol):
    category_scores: dict[Category, int | None]


class ScorecardView:
    def __init__(
        self,
        get_card_score: Callable[[], int],
        category_scores: dict[Category, int | None],
    ):
        self._card_get_score = get_card_score
        self.category_scores = category_scores

    def get_unscored_categories(self) -> list[Category]:
        return [c for c in self.category_scores if self.category_scores[c] is None]

    def get_card_score(self) -> int:
        return self._card_get_score()


class Scorecard:
    """Tracks the score for a single player."""

    def __init__(self):
        # Initialize all categories to None (not scored yet)
        self.category_scores: dict[Category, int | None] = {
            category: None for category in Category
        }
        self.yahtzee_bonus_count = 0

    def zero_category(self, category: Category, dice: list[int]) -> None:
        if self.category_scores[category] is not None:
            raise CategoryAlreadyScored(f"Category {category.name} has already been scored")
        self.category_scores[category] = 0

        # Award Yahtzee bonus if applicable
        if is_yahtzee(dice) and self.category_scores.get(Category.YAHTZEE) == 50:
            self.yahtzee_bonus_count += 1

    def set_category_score(self, category: Category, dice: list[int]) -> None:
        """Set score for specified category based on dice values."""

        #  --- Check for Input Errors  ---

        if category not in self.category_scores:
            raise InvalidCategoryError(f"Unknown category: {category}")

        if self.category_scores[category] is not None:
            raise CategoryAlreadyScored(f"Category {category.name} has already been scored")

        self._raise_on_invalid_dice(dice)

        # --- Validate playability ---
        if not is_playable(category, dice, self):
            raise InvalidCategoryError(f"Unplayable {category.name} combination: {dice}")

        # --- Begin Scoring Dice ---

        # Handle Yahtzee bonus first
        if is_yahtzee(dice) and self.category_scores[Category.YAHTZEE] == 50:
            self.yahtzee_bonus_count += 1

        # Call the appropriate scorer
        self.category_scores[category] = score(category, dice)

    def get_card_score(self) -> int:
        """Get the score across all categories including bonuses."""
        upper_score = sum(
            self.category_scores[cat] or 0 for cat in Category.get_upper_categories()
        )

        lower_score = sum(
            self.category_scores[cat] or 0 for cat in Category.get_lower_categories()
        )

        upper_bonus = UPPER_BONUS_SCORE if upper_score >= UPPER_BONUS_THRESHOLD else 0
        yahtzee_bonus = self.yahtzee_bonus_count * YAHTZEE_BONUS_SCORE

        return upper_score + upper_bonus + lower_score + yahtzee_bonus

    def get_unscored_categories(self) -> list[Category]:
        """Return a list of categories that have not been scored yet."""
        return [cat for cat, score in self.category_scores.items() if score is None]

    def _raise_on_invalid_dice(self, dice: list[int]) -> None:
        if len(dice) != 5:
            raise DiceCountError(f"Invalid dice count: {len(dice)}")
        if any(d < 1 or d > 6 for d in dice):
            raise DieValueError("The value of all dice must be between 1 and 6.")

    def __str__(self) -> str:
        scored = {
            cat.name: score for cat, score in self.category_scores.items() if score is not None
        }
        return f"Scorecard({scored}, bonuses={self.yahtzee_bonus_count})"

    @property
    def view(self) -> ScorecardView:
        """Return a read-only view of the scorecard."""
        return ScorecardView(self.get_card_score, dict(self.category_scores))
