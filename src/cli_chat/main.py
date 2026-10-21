import typer
from openai import OpenAI
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.formatted_text import HTML
from rich.console import Console

from cli_chat.commands.chat import handle_chat_message
from cli_chat.commands.handlers import COMMANDS
from cli_chat.commands.session import Session
from cli_chat.config import get_settings
from cli_chat.services.chat_service import ChatService
from cli_chat.storage.conversation_repository import init_db
from cli_chat.ui.panels import build_message_panel
from cli_chat.ui.theme import prompt_style, rich_theme

app = typer.Typer()


@app.command()
def main() -> None:
    settings = get_settings()
    console = Console(theme=rich_theme)
    chat_service = ChatService(OpenAI(api_key=settings.openai_api_key), model=settings.model)

    init_db()
    session = Session(
        console=console,
        chat_service=chat_service,
        settings=settings,
        conversation=chat_service.start_conversation(),
    )
    slash_completer = WordCompleter(list(COMMANDS), WORD=True)

    while session.is_running:
        user_input = prompt(
            HTML("<user-prompt>You ❯ </user-prompt>"),
            completer=slash_completer,
            complete_while_typing=True,
            style=prompt_style,
        )

        command_name = user_input.strip().lower()
        if not command_name:
            continue

        command = COMMANDS.get(command_name)
        if command is not None:
            command(session)
            continue

        console.print(build_message_panel(user_input))
        session.conversation = handle_chat_message(
            user_input, session.conversation, chat_service, console
        )


if __name__ == "__main__":
    app()
