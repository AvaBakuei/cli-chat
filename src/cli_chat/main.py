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


@app.command()
def main():
    settings = get_settings()
    console = Console(theme=rich_theme)
    chat_service = ChatService(
        OpenAI(api_key=settings.openai_api_key), model=settings.model)

    init_db()
    conversation = chat_service.start_conversation()

    current_page = 0
    current_selection = 1
    all_chats = []
    result_data = {}
    slash_completer = WordCompleter(
        ["/new", "/resume", "/delete", "/exit"], WORD=True)

    while True:
        user_input = prompt(
            HTML("<user-prompt>You ❯ </user-prompt>"),
            completer=slash_completer,
            complete_while_typing=True,
            style=prompt_style,
        )

        if not user_input.strip():
            continue

        if handle_exit_command(user_input, console):
            break

        if handle_new_command(user_input, console):
            conversation = chat_service.start_conversation()
            continue

        if handle_resume_command(user_input, console, settings.items_per_page,
                                 current_page, current_selection, all_chats, result_data):
            conversation = chat_service.get_conversation(
                result_data["selected_chat"])
            continue

        if handle_delete_command(user_input, console):
            continue

        console.print(build_message_panel(user_input))
        conversation = handle_chat_message(
            user_input, conversation, chat_service, console)


if __name__ == "__main__":
    app()
