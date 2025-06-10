# src/yaht/scorecard.py

from typing import Callable, Protocol

from yaht.category import Category
from yaht.dicetypes import DiceRoll
from yaht.exceptions import (
    CategoryAlreadyScored,
    InvalidCategoryError,
)
from yaht.scorecheck import calculate_combo_score, is_combo_scoreable

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

    def zero_category(self, category: Category, roll: DiceRoll) -> None:
        if self.category_scores[category] is not None:
            raise CategoryAlreadyScored(f"Category {category.name} has already been scored")
        self.category_scores[category] = 0

        # Award Yahtzee bonus if applicable
        if Category.YAHTZEE in roll and self.category_scores.get(Category.YAHTZEE) == 50:
            self.yahtzee_bonus_count += 1

    def set_category_score(self, category: Category, roll: DiceRoll) -> None:
        """Set score for specified category based on dice values."""

        #  --- Check for Input Errors  ---

        if category not in self.category_scores:
            raise InvalidCategoryError(f"Unknown category: {category}")

        if self.category_scores[category] is not None:
            raise CategoryAlreadyScored(f"Category {category.name} has already been scored")

        # --- Validate playability ---
        if not is_combo_scoreable(category, roll, self):
            raise InvalidCategoryError(f"Unplayable {category.name} combination: {roll}")

        # --- Begin Scoring Dice ---

        # Handle Yahtzee bonus first
        if Category.YAHTZEE in roll and self.category_scores[Category.YAHTZEE] == 50:
            self.yahtzee_bonus_count += 1

        # Call the appropriate scorer
        self.category_scores[category] = calculate_combo_score(category, roll)

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

    def __str__(self) -> str:
        scored = {
            cat.name: score for cat, score in self.category_scores.items() if score is not None
        }
        return f"Scorecard({scored}, bonuses={self.yahtzee_bonus_count})"

    @property
    def view(self) -> ScorecardView:
        """Return a read-only view of the scorecard."""
        return ScorecardView(self.get_card_score, dict(self.category_scores))
