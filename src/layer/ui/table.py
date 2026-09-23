from rich.table import Table
from datetime import datetime
from rich.console import Group
from rich.console import Console
from layer.ui.theme import custom_theme


console = Console(theme=custom_theme)


def draw_table(selected_index, data, has_back=False, has_more=False, page=0, items_per_page=10):
    table = Table(
        title="[title]List of Conversations[/title]", title_justify="left")
    table.add_column(
        "[column]ID[/column]", justify="left")
    table.add_column(
        "[column]Title[/column]", justify="left")
    table.add_column(
        "[column]Created at[/column]", justify="left")

    for index in range(len(data) + 2):
        style = "bold slate_blue1 on dark_olive_green1" if index == selected_index else "row"

        if index == 0:
            if has_back:
                table.add_row("back", "", "", style=style)
            else:
                table.add_row("", "", "", style="row")
            continue

        if index == len(data) + 1:
            if has_more:
                table.add_row("more", "", "", style=style)
            else:
                table.add_row("", "", "", style="row")
            continue
        created_at, title, item_id = data[index - 1]
        readable_date = datetime.fromtimestamp(
            created_at).strftime("%Y-%m-%d %H:%M")

        display_index = (page * items_per_page) + index

        table.add_row(str(display_index), title, readable_date, style=style)

    hint_text = "\n[dim]💡 Use [bold]↑/↓ Arrows[/bold] to navigate • Press [bold][Enter][/bold] to select • [bold]Ctrl+C[/bold] to exit[/dim]"
    return Group(table, hint_text)
