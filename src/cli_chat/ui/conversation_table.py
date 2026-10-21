from rich.table import Table
from datetime import datetime
from rich.console import Group

def build_conversation_table(selected_index, data, has_back=False, has_more=False, page=0, items_per_page=10):
    table = Table(
        title="[title]List of Conversations[/title]", title_justify="left")
    table.add_column(
        "[column]ID[/column]", justify="left")
    table.add_column(
        "[column]Title[/column]", justify="left")

    table.add_column("[column]Last activity[/column]",
                 justify="left")

    for index in range(len(data) + 2):
        style = "selected_row" if index == selected_index else "row"

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
        conversation = data[index - 1]
        readable_date = datetime.fromtimestamp(
            conversation.last_activity).strftime("%Y-%m-%d %H:%M")
        display_index = (page * items_per_page) + index
        table.add_row(str(display_index), conversation.title,
                      readable_date, style=style)

    hint_text = "\n[dim]💡 Use [bold]↑/↓ Arrows[/bold] to navigate • Press [bold][Enter][/bold] to select • [bold]Ctrl+C[/bold] to exit[/dim]"
    return Group(table, hint_text)
