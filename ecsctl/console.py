from datetime import datetime
from tabulate import tabulate
from typing import Any, List, Optional


def render_column(item: Any) -> str:
    if isinstance(item, datetime):
        return item.strftime("%Y/%m/%d %H:%M:%S")
    elif item is None:
        return ""
    else:
        return str(item)


class Color:
    YELLOW = "\u001b[33m"
    _RESET = "\u001b[0m"


class Console:
    def input(self, message: str) -> str:
        return input(message)

    def print(self, message: Any, color: Optional[Color] = None):
        reset = ""

        if color is not None:
            reset = Color._RESET

        print(f"{color or ''}{message}{reset}")

    def table(self, items: List[Any]):
        first = items[0]

        table_headers = [
            head.upper().replace("_", " ") for head in first.__class__.DEFAULT_COLUMNS
        ]
        table_body = [
            [
                render_column(row.__dict__[name])
                for name in row.__class__.DEFAULT_COLUMNS
            ]
            for row in items
        ]

        print(
            tabulate(
                table_body,
                headers=table_headers,
                tablefmt="plain",
                numalign="left",
                stralign="left",
            )
        )