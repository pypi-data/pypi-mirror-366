from __future__ import annotations

import re
from enum import StrEnum


class Markup(StrEnum):
    """Text format handling and markup language utilities."""

    MARKDOWN = "Markdown"
    MARKDOWN_V2 = "MarkdownV2"
    HTML = "HTML"

    def escape(self, text: str) -> str:
        """Escape special characters based on the current text type."""
        if self is Markup.MARKDOWN or self is Markup.MARKDOWN_V2:
            return self._escape_markdown(text)
        return self._escape_html(text) if self is Markup.HTML else text

    def clean(self, text: str) -> str:
        """Remove all formatting based on the current text type."""
        if self is Markup.MARKDOWN or self is Markup.MARKDOWN_V2:
            return self._strip_markdown(text)
        return self._strip_html(text) if self is Markup.HTML else text

    def _escape_markdown(self, text: str) -> str:
        if self not in {Markup.MARKDOWN, Markup.MARKDOWN_V2}:
            return text

        text = text.replace("\\", "\\\\")  # Handle actual backslashes first

        def escape(esc_text: str) -> str:
            esc_chars = [
                "\\.",
                "_",
                "-",
                r"\(",
                r"\)",
                r"\!",
                "<",
                ">",
                "#",
                r"\+",
                "~",
                r"\`",
                "|",
                "{",
                "}",
                "=",
                "[",
                "]",
            ]
            return re.sub(rf"(?<!\\)([{re.escape(''.join(esc_chars))}])", r"\\\1", esc_text)

        pattern = r"(```.*?```|`[^`\n]*`)|([^`]+|`)"
        escaped_text = []
        inside_code_block = False

        for match in re.finditer(pattern, text, re.DOTALL):
            if match.group(1):  # This is a code block
                escaped_text.append(match.group(1))
                if match.group(1).startswith("```") and match.group(1).endswith("```"):
                    inside_code_block = not inside_code_block
            else:  # This is non-code block text
                escaped_text.append(escape(match.group(2)))

        return "".join(escaped_text)

    def _strip_markdown(self, text: str) -> str:
        if self not in {Markup.MARKDOWN, Markup.MARKDOWN_V2}:
            return text

        escape_chars = "_*[]()~`>#+-=|{}.!"
        return re.sub(rf"([\\{escape_chars}])", r"", text)

    def _escape_html(self, text: str) -> str:
        if self != Markup.HTML:
            return text

        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;")
        )

    def _strip_html(self, text: str) -> str:
        return text if self != Markup.HTML else re.sub(r"<[^>]*>", "", text)
