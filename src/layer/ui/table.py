from rich.table import Table
from datetime import datetime
from rich.console import Group
from rich.console import Console
from src.cli.LocalRepository import show_conversation
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

    hint_text = "\n[dim]💡 Use [bold]↑/↓ Arrows[/bold] to navigate • Press Press [bold][Number][/bold] or [bold][Enter][/bold] to select • [bold]Ctrl+C[/bold] to exit[/dim]"
    return Group(table, hint_text)


def get_conversation_table(selected_conversation):
    # ---- Retrieve conversations from sql database based on conversation id
    chat_log = show_conversation(selected_conversation[2])
    table = Table(
        title=f"[title]{chat_log[1][2]}[/title]", title_justify="left")
    table.add_column(
        "[column]Role[/column]", justify="left")
    table.add_column(
        "[column]Content[/column]", justify="left")
    table.add_column(
        "[column]Created at[/column]", justify="left")
    for chat in chat_log:
        msg_id, conv_id, title, role, content, created_at = chat
        readable_date = datetime.fromtimestamp(
            created_at).strftime("%Y-%m-%d %H:%M")
        if role.lower() == "user":
            role_style = f"[input]{role}[/input]"
            content_style = f"[input]{content}[/input]"
            time_style = f"[input]{readable_date}[/input]"
        else:
            role_style = f"[output]{role}[/output]"
            content_style = f"[output]{content}[/output]"
            time_style = f"[output]{readable_date}[/output]"
        table.add_row(role_style, content_style, time_style)
    return table
