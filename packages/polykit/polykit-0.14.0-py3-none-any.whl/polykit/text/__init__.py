"""Stop wrestling with text manipulation and datetime formatting. Polykit's **Text** and **Time** utilities handle everything from pluralization to timezone-aware parsing:

```python
from polykit.text import Text

# Smart pluralization that just works
print(f"Found {Text.plural('file', 5, show_num=True)}")  # "Found 5 files"
print(f"Processing {Text.plural('class', 1, show_num=True)}")  # "Processing 1 class"

# Intelligent truncation with context preservation
long_text = "This is a very long text that needs to be shortened while preserving meaning..."
print(PolyTruncate.truncate(long_text, chars=50))  # Ends at sentence or word boundary
print(PolyTruncate.truncate(long_text, from_middle=True))  # Preserves start and end

# Terminal colors made simple
Text.print_color("Success!", color="green", style=["bold"])
Text.print_color("Warning!", color="yellow")
Text.print_color("Error!", color="red", style=["bold", "underline"])

# Battle-tested message splitting that handles even the trickiest edge cases
parts = Text.split_message(long_markdown, max_length=4096)  # Handles the toughest code blocks!
for part in parts:
    send_message(part)  # Perfect for APIs with message length limits
```

### Why These Utilities Make Development Nicer

- **Battle-Tested Reliability**: The message splitting function alone represents nearly a year of refinement through production use. It can survive almost anything—and it has.
- **Edge Case Mastery**: Handles even the most problematic scenarios like nested code blocks and special characters.
- **No More Pluralization Bugs**: Automatically handle singular/plural forms for cleaner messages.

These utilities solve real-world text and time challenges and have been hardened against some of the nastiest edge cases. My message splitting function alone represents nearly a year of refinement to handle every quirk of Markdown parsing that you really don't want to deal with—and now you don't have to!
"""  # noqa: D212, D415, W505

from __future__ import annotations

from .markup import Markup
from .text import Text
from .truncate import Truncate

color = Text.color
print_color = Text.print_color
truncate = Truncate.truncate
split = Text.split
plural = Text.plural
num_to_word = Text.to_word
ordinal = Text.ordinal
format_number = Text.format_number
