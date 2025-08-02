from __future__ import annotations

import contextlib
import re
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, ClassVar

from .types import COLOR_MAP, SMART_QUOTES_TABLE, STYLE_MAP, Colors

if TYPE_CHECKING:
    from .types import TextColor, TextStyle


class Text:
    """Text format handling and markup language utilities."""

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

    @staticmethod
    def color(
        text: Any,
        color: TextColor | None = None,
        style: TextStyle | None = None,
    ) -> str:
        """Return a string with the specified color and style attributes.

        Args:
            text: The text to colorize. If it's not a string, it'll try to convert to one.
            color: The name of the color. Has to be a color from ColorName.
            style: A list of attributes to apply to the text (e.g. ['bold', 'underline']).
        """
        text = str(text)  # Ensure text is a string

        # If no styling needed, return the original text
        if not color and not style:
            return text

        result = ""

        if style:  # Add styles
            for attr in style:
                if attr in STYLE_MAP:
                    result += STYLE_MAP[attr]

        if color:  # Add color
            if color in COLOR_MAP:
                result += COLOR_MAP[color]
            else:  # Try to get from our Colors enum (case-insensitive)
                with contextlib.suppress(AttributeError, TypeError):
                    result += getattr(Colors, color.upper(), "")

        # Add text and reset
        result += f"{text}{Colors.RESET}"
        return result

    @staticmethod
    def print_color(
        text: Any,
        color: TextColor | None = None,
        style: TextStyle | None = None,
        end: str = "\n",
    ) -> None:
        r"""Print a string with the specified color and style attributes.

        Args:
            text: The text to print in color. If it's not a string, it'll try to convert to one.
            color: The name of the color. Has to be a color from ColorName.
            style: A list of attributes to apply to the text (e.g. ['bold', 'underline']).
            end: The string to append after the last value. Defaults to "\n".
        """
        print(Text.color(str(text), color, style), end=end)

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

    @staticmethod
    def to_word(number: int) -> str:
        """Convert numbers 1-9 into their word equivalents.

        Args:
            number: The number to convert.

        Returns:
            The converted word or number.
        """
        return Text.NUM_WORDS.get(number, str(number))

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

    @staticmethod
    def format_number(
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
        `Text.plural` directly, unless you need additional formatting options.

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
            Text.format_number(2)                                   -> 2
            Text.format_number(2, "cat")                            -> cats
            Text.format_number(2, "cat", show_num=True)           -> 2 cats

            # As word
            Text.format_number(2, as_word=True)                     -> two
            Text.format_number(2, "cat", as_word=True)              -> two cats

            # As ordinal
            Text.format_number(2, as_ordinal=True)                  -> 2nd
            Text.format_number(2, "cat", as_ordinal=True)           -> 2nd cat

            # With commas
            Text.format_number(1000, commas=True)                   -> 1,000
            Text.format_number(1000, commas=False)                  -> 1000
            Text.format_number(1234567, "file", commas=True)        -> 1,234,567 files
            Text.format_number(1000, as_ordinal=True, commas=True)  -> 1,000th

            # And yes...
            Text.format_number(2, as_word=True, as_ordinal=True)    -> twond
            ```
        """
        # Combine word numbers with ordinals, because it's what you asked for!
        if as_word and as_ordinal and number in Text.NUM_WORDS:
            ordinal_suffix = Text.ordinal(number).replace(str(number), "")
            num_str = f"{Text.NUM_WORDS[number]}{ordinal_suffix}"  # e.g. "twond", "threerd"
        elif as_ordinal:
            if commas:  # Format number with commas, then add ordinal suffix
                formatted_number = f"{number:,}"
                ordinal_suffix = Text.ordinal(number).replace(str(number), "")
                num_str = f"{formatted_number}{ordinal_suffix}"
            else:
                num_str = Text.ordinal(number)
        elif as_word and number in Text.NUM_WORDS:
            num_str = Text.NUM_WORDS[number]
        else:
            num_str = f"{number:,}" if commas else str(number)

        if word:  # Handle word if provided
            if as_ordinal:
                result = f"{num_str} {word}"
            else:
                pluralized = Text.plural(word, number, show_num=False)
                result = f"{num_str} {pluralized}" if show_num else pluralized
        else:
            result = num_str

        return result

    @staticmethod
    def straighten_quotes(text: str) -> str:
        """Replace smart quotes with straight quotes."""
        return text.translate(SMART_QUOTES_TABLE)

    @staticmethod
    def normalize(text: str) -> str:
        """Normalize text by stripping whitespace, multiple spaces, and normalizing quotes."""
        text = Text.straighten_quotes(text)
        text = text.strip()
        return " ".join(text.split())

    @staticmethod
    def clean_newlines(text: str, leave_one: bool = True) -> str:
        """Clean up excessive newlines in text.

        Args:
            text: The text to clean.
            leave_one: If True, leaves one newline between paragraphs.
                       Otherwise leaves no blank lines. Defaults to True.
        """
        while "\n\n\n" in text:
            text = text.replace("\n\n\n", "\n\n" if leave_one else "\n")
        return text

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

    @staticmethod
    def split(message: str, max_length: int = 4096) -> list[str]:
        """Split a message into smaller parts for Telegram, handling Markdown and code blocks.

        This method splits long messages into smaller parts for sending as Telegram messages. It
        handles many different edge cases, particularly with respect to code blocks. It's the bee's
        knees, refined over many months and now battle-tested and extremely reliable.
        """

        if len(message) <= max_length:
            return [message]

        split_points = {
            "paragraph": re.compile(r"\n\n"),
            "line": re.compile(r"\n"),
            "sentence": re.compile(r"(?<=\.)\s+"),
            "space": re.compile(r" "),
        }

        split_point = None
        code_block_language = ""

        for pattern in split_points.values():
            split_point = Text._find_split_point(message, pattern, max_length)
            if split_point:
                break

        if not split_point:
            split_point, code_block_language = Text._split_by_code_blocks(message, max_length)

        part1 = message[:split_point].rstrip()
        part2 = message[split_point:].lstrip()

        if not Text._is_balanced_code_blocks(part1):
            part1 += "```"
            part2 = f"```{code_block_language}\n{part2}"

        return [part1, *Text.split(part2, max_length)]

    @staticmethod
    def _find_split_point(text: str, pattern: re.Pattern[Any], max_len: int) -> int | None:
        matches = list(pattern.finditer(text[:max_len]))
        if not matches:
            return None

        split_point = matches[-1].start()

        # Check for Markdown headers or styled text at the beginning of the next line
        next_line_start = text.find("\n", split_point)
        if next_line_start != -1 and next_line_start + 1 < len(text):
            next_char = text[next_line_start + 1]
            # Move the split point to before the newline
            if next_char in "#*":
                return next_line_start

        return split_point

    @staticmethod
    def _split_by_code_blocks(text: str, max_len: int) -> tuple[int, str]:
        code_block_indices = [m.start() for m in re.finditer(r"```", text)]
        code_block_language = ""

        # If there's a code block marker before max_len, try to use it as split point
        for index in code_block_indices:
            if index < max_len:
                split_point = index + 3  # Include the ```
                # Only use this point if it results in balanced code blocks
                if Text._is_balanced_code_blocks(text[:split_point]):
                    break
        else:  # No suitable code block split found
            split_point = max_len
            # Adjust split point to avoid breaking within backticks
            while split_point > 0 and text[split_point - 1] == "`":
                split_point -= 1
            while split_point < len(text) and text[split_point] == "`":
                split_point += 1
            split_point = min(split_point, len(text))

        # If we split within a code block, capture its language
        if "```" in text[:split_point]:
            start_of_block = text.rfind("```", 0, split_point)
            end_of_block = text.find("\n", start_of_block)
            if end_of_block != -1:
                code_block_language = text[start_of_block + 3 : end_of_block].strip()

        return split_point, code_block_language

    @staticmethod
    def _is_balanced_code_blocks(text: str) -> bool:
        return text.count("```") % 2 == 0

    @staticmethod
    def is_emoji(char: str) -> bool:
        """Check if a string is an emoji."""
        if not char:
            return False

        code = ord(char)
        return (
            0x1F600 <= code <= 0x1F64F  # Emoticons
            or 0x1F300 <= code <= 0x1F5FF  # Misc Symbols and Pictographs
            or 0x1F680 <= code <= 0x1F6FF  # Transport and Map
            or 0x1F1E0 <= code <= 0x1F1FF  # Regional indicators
            or 0x2600 <= code <= 0x26FF  # Misc symbols
            or 0x2700 <= code <= 0x27BF  # Dingbats
            or 0xFE00 <= code <= 0xFE0F  # Variation Selectors
            or 0x1F900 <= code <= 0x1F9FF  # Supplemental Symbols and Pictographs
            or 0x1F018 <= code <= 0x1F270  # Various symbols
            or 0x238C <= code <= 0x2454  # Misc symbols
            or 0x20D0 <= code <= 0x20FF  # Combining marks for symbols
            or 0x2B00 <= code <= 0x2BFF  # Additional symbols
        )

    @staticmethod
    def starts_with_emoji(text: str) -> bool:
        """Check if a string starts with an emoji."""
        if not text:
            return False

        return Text.is_emoji(text[0])

    @staticmethod
    def extract_first_emoji(text: str) -> str:
        """Extract the first emoji from a string."""
        return "" if not text or not Text.starts_with_emoji(text) else text[0]
