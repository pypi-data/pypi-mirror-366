from __future__ import annotations

import sys
import traceback
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import types

try:
    from pygments import highlight
    from pygments.formatters import TerminalFormatter
    from pygments.lexers import PythonTracebackLexer

    pygments_available = True
except ImportError:
    pygments_available = False


def log_traceback(
    exc_type: type[BaseException] | None = None,
    exc_value: BaseException | None = None,
    exc_tb: types.TracebackType | None = None,
    trim_levels: int = 0,
) -> None:
    """Log a traceback, optionally trimming unwanted levels."""
    if exc_type is None or exc_value is None or exc_tb is None:
        exc_type, exc_value, exc_tb = sys.exc_info()

    # Trim traceback to set number of levels
    for _ in range(trim_levels):
        if exc_tb is not None:
            exc_tb = exc_tb.tb_next

    # Log traceback and exception details
    if exc_value is not None and exc_tb is not None:
        tb_list = traceback.format_exception(exc_type, exc_value, exc_tb)
        tb = "".join(tb_list)
        if pygments_available:
            tb = highlight(tb, PythonTracebackLexer(), TerminalFormatter())
        else:
            print("Can't colorize traceback because Pygments is not installed.")
        sys.stderr.write(tb)
