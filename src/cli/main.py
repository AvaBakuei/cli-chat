import os
import typer
import sys
from dotenv import load_dotenv
from openai import OpenAI
from rich.console import Console
from rich.theme import Theme
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.console import Group
from readchar import readkey, key
from datetime import datetime
from database import init_db, save_conversations, get_all_conversations, delete_all_conversations, show_conversation

load_dotenv()

app = typer.Typer()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
conversation = client.conversations.create()

custom_theme = Theme({
    "prompt": "bold cyan",
    "loading": "chartreuse2",
    "input": "bold magenta",
    "output": "bold red",
    "info": "bold yellow",
    "column": "green_yellow",
    "row": "bold slate_blue1",
    "title": "bold medium_orchid1"
})

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


def retrieve_conversation(selected_conversation):
    # ---- Retrieve conversations from sql database based on conversation id
    chat_log = show_conversation(selected_conversation[2])
    print("selected_conversation", selected_conversation)
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
    print(f"DEBUG: Found {len(chat_log)} messages for this chat.")
    return console.print(table)


@app.command()
def main():
    init_db()
    global conversation
    ITEMS_PER_PAGE = 10
    current_page = 0
    current_selection = 1
    all_chats = []

    while True:
        user_input = console.input(
            "[prompt]You ❯ [/prompt]")

        # ---- Exit form chat
        if user_input.strip().lower() == "/exit":
            console.print("[info]Goodbye![/info]")
            break

        if not user_input.strip():
            continue

        # ---- Create new chat
        if user_input.strip().lower() == "/new":
            conversation = client.conversations.create()
            console.clear()
            console.print(
                "\n[info]System Chat history cleared. Starting a fresh conversation![/info]")
            continue

        # ---- Show a list of conversations:
        if user_input.strip().lower() == "/resume":
            all_chats = get_all_conversations()
            if not all_chats:
                console.print(
                    "[info]💬 This conversation is empty. Type a message to get started![/info]")
                continue

            with Live(draw_table([], []), console=console, auto_refresh=False, transient=True) as live:
                while True:
                    start_index = current_page * ITEMS_PER_PAGE
                    end_index = start_index + ITEMS_PER_PAGE

                    page_data = all_chats[start_index:end_index]

                    has_back = current_page > 0
                    has_more = end_index < len(all_chats)

                    live.update(draw_table(current_selection,
                                           page_data, has_back, has_more, page=current_page, items_per_page=ITEMS_PER_PAGE), refresh=True)

                    pressed = readkey()
                    if pressed == key.UP:
                        current_selection = max(0, current_selection - 1)
                    elif pressed == key.DOWN:
                        current_selection = min(
                            len(page_data) + 1, current_selection + 1)
                    elif pressed == key.ENTER:
                        if current_selection == 0 and has_back:
                            current_page -= 1
                            current_selection = start_index
                        elif current_selection == len(page_data) + 1 and has_more:
                            current_page += 1
                            current_selection = 1
                        elif 1 <= current_selection <= len(page_data):
                            actual_chat_index = start_index + \
                                (current_selection - 1)
                            selected_chat = all_chats[actual_chat_index]
                            retrieve_conversation(selected_chat)
                            break
                    elif pressed.isdigit:
                        selection = int(pressed)
                        retrieve_conversation(all_chats[selection - 1])
                        break

                    elif pressed == key.CTRL_C:
                        sys.exit(0)

            continue

        # ---- Delete all of conversations:
        if user_input.strip().lower() == "/delete":
            delete_all_conversations()
            console.print(
                "[info]💥 All conversations have been permanently deleted![/info]")

            continue

        combined_input_text = f"[input]{user_input}[/input]"
        console.print(Panel(combined_input_text, title="[input]User[/input]",
                            border_style="input"))
        is_first_turn_of_chat = "title" not in conversation.metadata

        if is_first_turn_of_chat:
            title_response = client.responses.create(
                model="gpt-6-astra",
                instructions="You are a utility that generates short titles for chat logs. Summarize the user's request in 3 to 5 words. Do not use quotes, punctuation, or prefix words like 'Title:'.",
                input=[{"role": "user", "content": user_input}]
            )
            client_title = title_response.output_text

            conversation = client.conversations.update(
                conversation_id=conversation.id,
                metadata={"title": client_title}
            )

        save_conversations(
            conversation.id, client_title, "user", user_input, conversation.created_at)

        with console.status("[loading]Thinking... [/loading]"):
            response = client.responses.create(
                model="gpt-6-astra",
                input=[{"role": "user", "content": user_input}],
                conversation=conversation.id
            )
        chat_output = response.output_text

        save_conversations(conversation.id, client_title,
                           "assistant", chat_output, conversation.created_at)

        combined_output_text = f"[output]{chat_output}[/output]"
        console.print(Panel(combined_output_text,
                            title="[output]ChatGPT[/output]", border_style="output"))


if __name__ == "__main__":
    app()
