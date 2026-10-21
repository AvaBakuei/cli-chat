from datetime import datetime

from rich.console import Group
from rich.table import Table

COLUMNS = ("ID", "Title", "Last activity")
DATE_FORMAT = "%Y-%m-%d %H:%M"
HINT_TEXT = (
    "\n[dim]💡 Use [bold]↑/↓ Arrows[/bold] to navigate • "
    "Press [bold][Enter][/bold] to select • [bold]Ctrl+C[/bold] to exit[/dim]"
)


def build_conversation_table(selected_index, data, has_back=False, has_more=False, page=0, items_per_page=10):
    table = Table(
        title="[title]List of Conversations[/title]", title_justify="left")
    for name in COLUMNS:
        table.add_column(f"[column]{name}[/column]")

    _add_navigation_row(table, "back", has_back,
                        is_selected=selected_index == 0)

    for position, conversation in enumerate(data, start=1):
        last_activity = datetime.fromtimestamp(
            conversation.last_activity).strftime(DATE_FORMAT)
        display_index = page * items_per_page + position
        table.add_row(
            str(display_index),
            conversation.title,
            last_activity,
            style=_row_style(selected_index == position),
        )

    _add_navigation_row(table, "more", has_more,
                        is_selected=selected_index == len(data) + 1)

    return Group(table, HINT_TEXT)


def _row_style(is_selected: bool) -> str:
    return "selected_row" if is_selected else "row"


def _add_navigation_row(table: Table, label: str, is_visible: bool, is_selected: bool) -> None:
    if is_visible:
        table.add_row(label, "", "", style=_row_style(is_selected))
    else:
        table.add_row("", "", "", style="row")
