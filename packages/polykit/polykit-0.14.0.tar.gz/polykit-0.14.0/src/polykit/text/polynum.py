from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any, ClassVar

from polykit.core.deprecate import deprecated


class PolyNum:
    """Text utilities for working with numbers and pluralization.

    Provides methods for intelligent pluralization of words based on counts, converting numbers to
    their word equivalents, and formatting numeric text for better readability. Handles edge cases
    like words ending in 's' and supports both counted and uncounted pluralization scenarios.
    """

    NUM_WORDS: ClassVar[dict[int, str]] = {
        0: "zero",
        1: "one",
        2: "two",
        3: "three",
        4: "four",
        5: "five",
        6: "six",
        7: "seven",
        8: "eight",
        9: "nine",
    }

    @deprecated("Use Text class instead.")
    @staticmethod
    def plural(word: str, count: int, show_num: bool = True, commas: bool = True) -> str:
        """Pluralize a word based on the count of items.

        Args:
            word: The word to pluralize.
            count: The number of items, which determines the pluralization.
            show_num: Whether to include the count number before the word. Defaults to True.
            commas: Whether to add commas to the count number. Defaults to True.

        Returns:
            The pluralized word with optional count.
        """
        if count == 1:
            return f"1 {word}" if show_num else word
        if show_num:
            if word.endswith("s"):
                return f"{count:,} {word}es" if commas else f"{count} {word}es"
            return f"{count:,} {word}s" if commas else f"{count} {word}s"
        return f"{word}es" if word.endswith("s") else f"{word}s"

    @deprecated("Use Text class instead.")
    @staticmethod
    def to_word(number: int) -> str:
        """Convert numbers 1-9 into their word equivalents.

        Args:
            number: The number to convert.

        Returns:
            The converted word or number.
        """
        return PolyNum.NUM_WORDS.get(number, str(number))

    @deprecated("Use Text class instead.")
    @staticmethod
    def ordinal(n: int) -> str:
        """Convert an integer into its ordinal representation.

        Args:
            n: An integer number.

        Returns:
            The ordinal string of the integer, e.g., '1st', '2nd', '3rd', etc.
        """
        suffix = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
        return f"{n}{suffix}"

    @deprecated("Use Text class instead.")
    @staticmethod
    def format(
        number: int,
        word: str | None = None,
        *,
        show_num: bool = True,
        as_word: bool = False,
        as_ordinal: bool = False,
        commas: bool = True,
    ) -> str:
        """Format a number with various options for text representation.

        This method provides a flexible way to format numbers with optional word and ordinal
        representations, as well as the ability to include or exclude the number itself. It's
        recommended NOT to use this method solely for pluralization. It's simpler to just use
        `PolyNum.plural` directly, unless you need additional formatting options.

        Args:
            number: The number to format.
            word: Optional word to append (will be pluralized if needed).
            show_num: Include the number with the word. Defaults to True.
            as_word: Convert numbers 0-9 to words ("one", "two", etc.). Defaults to False.
            as_ordinal: Convert to ordinal form ("1st", "2nd", etc.). Defaults to False.
            commas: Add thousands separators to numbers. Defaults to True.

        NOTE: Setting BOTH `as_word` AND `as_ordinal` WILL work, giving you words like "twond" and
        "threerd". This is not a bug, it's a feature. It's literally what you asked for.

        Examples:
            ```python
            PolyNum.format(2)                                   -> 2
            PolyNum.format(2, "cat")                            -> cats
            PolyNum.format(2, "cat", show_num=True)           -> 2 cats

            # As word
            PolyNum.format(2, as_word=True)                     -> two
            PolyNum.format(2, "cat", as_word=True)              -> two cats

            # As ordinal
            PolyNum.format(2, as_ordinal=True)                  -> 2nd
            PolyNum.format(2, "cat", as_ordinal=True)           -> 2nd cat

            # With commas
            PolyNum.format(1000, commas=True)                   -> 1,000
            PolyNum.format(1000, commas=False)                  -> 1000
            PolyNum.format(1234567, "file", commas=True)        -> 1,234,567 files
            PolyNum.format(1000, as_ordinal=True, commas=True)  -> 1,000th

            # And yes...
            PolyNum.format(2, as_word=True, as_ordinal=True)    -> twond
            ```
        """
        # Combine word numbers with ordinals because it's hilarious and you asked for it
        if as_word and as_ordinal and number in PolyNum.NUM_WORDS:
            ordinal_suffix = PolyNum.ordinal(number).replace(str(number), "")
            num_str = f"{PolyNum.NUM_WORDS[number]}{ordinal_suffix}"  # e.g. "twond", "threerd"
        elif as_ordinal:
            if commas:  # Format number with commas, then add ordinal suffix
                formatted_number = f"{number:,}"
                ordinal_suffix = PolyNum.ordinal(number).replace(str(number), "")
                num_str = f"{formatted_number}{ordinal_suffix}"
            else:
                num_str = PolyNum.ordinal(number)
        elif as_word and number in PolyNum.NUM_WORDS:
            num_str = PolyNum.NUM_WORDS[number]
        else:
            num_str = f"{number:,}" if commas else str(number)

        if word:  # Handle word if provided
            if as_ordinal:
                result = f"{num_str} {word}"
            else:
                pluralized = PolyNum.plural(word, number, show_num=False)
                result = f"{num_str} {pluralized}" if show_num else pluralized
        else:
            result = num_str

        return result

    @deprecated("Use Text class instead.")
    @staticmethod
    def list_ids(ids: list[int] | list[str]) -> str:
        """Format a list of IDs as a string with commas and 'and'."""
        if not ids:
            return ""
        if len(ids) == 1:
            return str(ids[0])
        if len(ids) == 2:
            return f"{ids[0]} and {ids[1]}"
        return ", ".join(map(str, ids[:-1])) + ", and " + str(ids[-1])

    @deprecated("Use Text class instead.")
    @staticmethod
    def join_ids(ids: Any, separator: str = ", ") -> str:
        """Join any iterable of IDs into a string.

        Args:
            ids: An iterable (list, set, tuple, etc.) of IDs, or a single value.
            separator: The separator to use between IDs. Defaults to ', '.

        Returns:
            A string of joined IDs.

        Examples:
            ```python
            join_ids({1, 2, 3}) -> '1, 2, 3'
            join_ids([1, '2', 3.0]) -> '1, 2, 3.0'
            join_ids(123) -> '123'
            join_ids(range(3)) -> '0, 1, 2'
            ```
        """
        # If input is not iterable, convert to a single-item list
        if not isinstance(ids, Iterable) or isinstance(ids, str):
            ids = [ids]

        # Convert all elements to strings and join
        return separator.join(str(join_id) for join_id in ids)

    @deprecated("Use Text class instead.")
    @staticmethod
    def parse_ratio_input(user_input: str) -> float:
        """Parse user input for a ratio value from a percentage, ratio, or multiplier.

        Valid inputs include:
            - Percentages: '30%', '30 %', '30.5%'
            - Ratios: '0.3', '.3', '1.5'
            - Multipliers: '1.5x', '2X'
            - Whole numbers: '30' (treated as percentage)

        Raises:
            ValueError: If the input is invalid or out of acceptable range.

        Returns:
            The parsed ratio value as a float.
        """
        # Remove any whitespace and convert to lowercase
        cleaned_input = user_input.strip().lower()

        # Define regex patterns
        percentage_pattern = r"^(\d+(\.\d+)?)\s*%$"
        multiplier_pattern = r"^(\d+(\.\d+)?)\s*x$"
        number_pattern = r"^(\d+(\.\d+)?)$"

        try:
            if match := re.match(percentage_pattern, cleaned_input):  # Percentage input
                ratio_value = float(match[1]) / 100
            elif match := re.match(multiplier_pattern, cleaned_input):  # Multiplier input
                ratio_value = float(match[1])
            elif match := re.match(number_pattern, cleaned_input):  # Direct number input
                ratio_value = float(match[1])
                # If it's a whole number greater than 1, treat as percentage
                if ratio_value > 1 and ratio_value.is_integer():
                    ratio_value /= 100
            else:
                msg = "Invalid input format"
                raise ValueError(msg)

        except ValueError as e:
            msg = (
                "Invalid format. Please enter a valid number, "
                "a percentage (e.g., 20 or 20%), "
                "or a multiplier (e.g., 2 or 2x)."
            )
            raise ValueError(msg) from e

        # Validate the range
        if ratio_value < 0:
            msg = "The ratio must be a non-negative value"
            raise ValueError(msg)
        if ratio_value > 100:
            msg = "The ratio exceeds the maximum allowed value of 10000% (100x)"
            raise ValueError(msg)

        return ratio_value
