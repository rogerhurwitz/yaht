# src/yaht/scorecard.py
from enum import Enum, auto
from collections import Counter
from typing import Callable
from yaht.exceptions import CategoryAlreadyScored, DiceCountError, DieValueError, InvalidCategoryError

UPPER_BONUS_SCORE = 35
UPPER_BONUS_THRESHOLD = 63
YAHTZEE_BONUS_SCORE = 100

class Category(Enum):
    ACES = auto()
    TWOS = auto()
    THREES = auto()
    FOURS = auto()
    FIVES = auto()
    SIXES = auto()
    THREE_OF_A_KIND = auto()
    FOUR_OF_A_KIND = auto()
    FULL_HOUSE = auto()
    SMALL_STRAIGHT = auto()
    LARGE_STRAIGHT = auto()
    YAHTZEE = auto()
    CHANCE = auto()

class Scorecard:
    """Tracks the score for a single player."""
    def __init__(self):
        # Initialize all categories to None (not scored yet)
        self.scores: dict[Category, int | None]= {category: None for category in Category}
        self.yahtzee_bonus_count = 0
        
    def set_category_score(self, category: Category, dice: list[int] | None) -> None:
        """Set score based on category and dice. If dice is None then zero category."""

        #  --- Check for Input Errors  ---

        if category not in self.scores:
            raise InvalidCategoryError(f"Unknown category: {category}")

        if self.scores[category] is not None:
            raise CategoryAlreadyScored(f"Category {category.name} has already been scored")   

        # Validate number and value of dice or zero out category
        if dice:
            if len(dice) != 5:
                raise DiceCountError(f"Invalid dice count: {len(dice)}")
            if any(die < 1 or die > 6 for die in dice):
                raise DieValueError(f"Die value is not between 1 and 6")
        else:
            self.scores[category] = 0
            return
        
       # --- Apply Joker Rules ---

        if self._is_yahtzee(dice) and self.scores[Category.YAHTZEE] is not None:
            matching_upper = {
                1: Category.ACES,
                2: Category.TWOS,
                3: Category.THREES,
                4: Category.FOURS,
                5: Category.FIVES,
                6: Category.SIXES,
            }[dice[0]]

            if self.scores[matching_upper] is None and category != matching_upper:
                raise InvalidCategoryError(
                    f"Must score Yahtzee in {matching_upper.name} before choosing another category."
                )

        # --- Begin Scoring Dice ---
        
        dice_counts = Counter(dice)

        scoring_dispatch: dict[Category, Callable[[], int]] = {
            Category.ACES: lambda: self._score_upper_section(Category.ACES, dice),
            Category.TWOS: lambda: self._score_upper_section(Category.TWOS, dice),
            Category.THREES: lambda: self._score_upper_section(Category.THREES, dice),
            Category.FOURS: lambda: self._score_upper_section(Category.FOURS, dice),
            Category.FIVES: lambda: self._score_upper_section(Category.FIVES, dice),
            Category.SIXES: lambda: self._score_upper_section(Category.SIXES, dice),
            Category.THREE_OF_A_KIND: lambda: self._score_three_of_a_kind(dice, dice_counts),
            Category.FOUR_OF_A_KIND: lambda: self._score_four_of_a_kind(dice, dice_counts),
            Category.FULL_HOUSE: lambda: self._score_full_house(dice_counts),
            Category.SMALL_STRAIGHT: lambda: self._score_small_straight(dice),
            Category.LARGE_STRAIGHT: lambda: self._score_large_straight(dice),
            Category.YAHTZEE: lambda: self._score_yahtzee(dice),
            Category.CHANCE: lambda: self._score_chance(dice),
        }

        # call the appropriate scorer
        score = scoring_dispatch[category]()
        self.scores[category] = score
        
        # Handle Yahtzee bonus
        if (self._is_yahtzee(dice) and 
            category != Category.YAHTZEE and 
            self.scores[Category.YAHTZEE] == 50):
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
            Category.ACES, Category.TWOS, Category.THREES,
            Category.FOURS, Category.FIVES, Category.SIXES
        ]
        upper_score = sum(self.get_category_score(cat) for cat in upper_section)
        
        # Add upper section bonus if applicable
        upper_bonus = UPPER_BONUS_SCORE if upper_score >= UPPER_BONUS_THRESHOLD else 0
        
        # Calculate lower section score
        lower_section = [
            Category.THREE_OF_A_KIND, Category.FOUR_OF_A_KIND,
            Category.FULL_HOUSE, Category.SMALL_STRAIGHT,
            Category.LARGE_STRAIGHT, Category.YAHTZEE,
            Category.CHANCE
        ]
        lower_score = sum(self.get_category_score(cat) for cat in lower_section)
        
        # Add Yahtzee bonus
        yahtzee_bonus = self.yahtzee_bonus_count * YAHTZEE_BONUS_SCORE
        
        # Return total score
        return upper_score + upper_bonus + lower_score + yahtzee_bonus
    
    
    def _count_dice(self, dice: list[int]) -> dict[int, int]:
        """Count occurrences of each die value."""
        counts = {i: 0 for i in range(1, 7)}
        for die in dice:
            counts[die] += 1
        return counts
    
    def _is_yahtzee(self, dice: list[int]) -> bool:
        """Check if all dice have the same value (Yahtzee)."""
        return len(set(dice)) == 1
    
    def _score_upper_section(self, category: Category, dice: list[int]) -> int:
        target = {
            Category.ACES: 1,
            Category.TWOS: 2,
            Category.THREES: 3,
            Category.FOURS: 4,
            Category.FIVES: 5,
            Category.SIXES: 6,
        }[category]
        return sum(d for d in dice if d == target)

    def _score_three_of_a_kind(self, dice: list[int], counts: Counter) -> int:
        return sum(dice) if any(c >= 3 for c in counts.values()) else 0

    def _score_four_of_a_kind(self, dice: list[int], counts: Counter) -> int:
        return sum(dice) if any(c >= 4 for c in counts.values()) else 0

    def _score_full_house(self, counts: Counter) -> int:
        count_vals = sorted(counts.values(), reverse=True)
        return 25 if count_vals in ([5], [3, 2]) else 0

    def _score_small_straight(self, dice: list[int]) -> int:
        unique = set(dice)
        straights = [{1, 2, 3, 4}, {2, 3, 4, 5}, {3, 4, 5, 6}]
        return 30 if any(s.issubset(unique) for s in straights) else 0

    def _score_large_straight(self, dice: list[int]) -> int:
        return 40 if set(dice) in ({1, 2, 3, 4, 5}, {2, 3, 4, 5, 6}) else 0

    def _score_yahtzee(self, dice: list[int]) -> int:
        return 50 if self._is_yahtzee(dice) else 0

    def _score_chance(self, dice: list[int]) -> int:
        return sum(dice)