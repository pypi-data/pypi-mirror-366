"""
Rich error message printing.

Source: https://github.com/fastapi/typer/blob/master/typer/rich_utils.py
"""

from gettext import gettext
from os import getenv
from typing import Literal, Optional

from rich.console import Console
from rich.panel import Panel
from rich.theme import Theme


ALIGN_ERRORS_PANEL: Literal["left", "center", "right"] = "left"
_TERMINAL_WIDTH: str | None = getenv("TERMINAL_WIDTH")
MAX_WIDTH: int | None = int(_TERMINAL_WIDTH) if _TERMINAL_WIDTH else None
COLOR_SYSTEM: Optional[Literal["auto", "standard", "256", "truecolor", "windows"]] = (
    "auto"  # Set to None to disable colors
)
FORCE_TERMINAL: None | Literal[True] = (
    True
    if getenv(key="GITHUB_ACTIONS") or getenv("FORCE_COLOR") or getenv("PY_COLORS")
    else None
)

# Fixed strings
ERRORS_PANEL_TITLE: str = gettext("Error")


def _get_rich_console(stderr: bool = False) -> Console:
    return Console(
        theme=Theme(
            {
                "option": "bold cyan",
                "switch": "bold green",
                "negative_option": "bold magenta",
                "negative_switch": "bold red",
                "metavar": "bold yellow",
                "metavar_sep": "dim",
                "usage": "yellow",
            },
        ),
        color_system="auto",
        force_terminal=FORCE_TERMINAL,
        width=MAX_WIDTH,
        stderr=stderr,
    )


def _print_message(message: str, color: str) -> None:
    """
    Print a message in a panel with a colored border.

    Args:
        message (str): The message to display.
        color (str): The color of the border.
    """
    console: Console = _get_rich_console(stderr=True)
    console.print(
        Panel(
            renderable=message,
            border_style=color,
            title=ERRORS_PANEL_TITLE,
            title_align=ALIGN_ERRORS_PANEL,
        )
    )


def print_error_message(error_message: str) -> None:
    """
    Print an error message in red text.

    Args:
        error_message (str): The error message to display.
    """
    _print_message(message=error_message, color="red")


def print_warning_message(warning_message: str) -> None:
    """
    Print a warning message in yellow text.

    Args:
        warning_message (str): The warning message to display.
    """
    _print_message(message=warning_message, color="yellow")


def print_info_message(info_message: str) -> None:
    """
    Print an info message in blue text.

    Args:
        info_message (str): The info message to display.
    """
    _print_message(message=info_message, color="blue")
