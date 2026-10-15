import typer
from openai import OpenAI
from rich.console import Console
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.formatted_text import HTML
from cli.config import get_settings
from layer.ui.theme import rich_theme, prompt_style
from cli.conversation_repository import init_db
from layer.commands import handle_new_command, handle_resume_command, handle_delete_command, handle_exit_command
from layer.ui.panels import build_message_panel
from cli.chat_service import send_message


app = typer.Typer()
client = OpenAI(api_key=get_settings().openai_api_key)
conversation = client.conversations.create()


console = Console(theme=rich_theme)


@app.command()
def main():
    init_db()
    global conversation
    items_per_page = get_settings().items_per_page
    current_page = 0
    current_selection = 1
    all_chats = []
    result_data = {}

    slash_completer = WordCompleter(
        ["/new", "/resume", "/delete", "/exit"], WORD=True)
    while True:
        user_input = prompt(
            HTML('<user-prompt>You ❯ </user-prompt>'),
            completer=slash_completer,
            complete_while_typing=True,
            style=prompt_style
        )

        if not user_input.strip():
            continue

        # ---- Exit form chat
        if handle_exit_command(user_input, console):
            break

        # ---- Create new chat
        if handle_new_command(user_input, console):
            conversation = client.conversations.create()
            continue

        # ---- Show a list of conversations:
        if handle_resume_command(user_input, console, items_per_page, current_page, current_selection, all_chats, result_data):
            conversation.id = result_data.get("selected_chat")
            continue

        # ---- Delete all of conversations:
        if handle_delete_command(user_input, console):
            continue

        user_panel = build_message_panel(user_input)
        console.print(user_panel)

        send_message(user_input, conversation, console)


if __name__ == "__main__":
    app()
