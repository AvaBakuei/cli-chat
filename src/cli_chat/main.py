import typer
from openai import OpenAI
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.formatted_text import HTML
from rich.console import Console

from cli_chat.commands.chat import handle_chat_message
from cli_chat.commands.handlers import (
    handle_delete_command,
    handle_exit_command,
    handle_new_command,
    handle_resume_command,
)
from cli_chat.config import get_settings
from cli_chat.services.chat_service import ChatService
from cli_chat.storage.conversation_repository import init_db
from cli_chat.ui.panels import build_message_panel
from cli_chat.ui.theme import prompt_style, rich_theme

app = typer.Typer()
client = OpenAI(api_key=get_settings().openai_api_key)
chat_service = ChatService(client, model=get_settings().model)
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

        handle_chat_message(user_input, conversation, chat_service, console)
