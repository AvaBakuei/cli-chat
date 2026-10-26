import logging

import openai
import typer
from openai import OpenAI
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.formatted_text import HTML
from rich.console import Console

from cli_chat.commands.chat import handle_chat_message
from cli_chat.commands.handlers import COMMANDS, exit_command
from cli_chat.commands.session import Session
from cli_chat.config import LOG_PATH, ConfigError, get_settings
from cli_chat.services.chat_service import ChatService
from cli_chat.storage.conversation_repository import init_db
from cli_chat.ui.panels import build_message_panel
from cli_chat.ui.theme import prompt_style, rich_theme

STARTUP_CONNECTION_ERROR_TEXT = (
    "⚠️ Could not connect to OpenAI. Check your internet connection and API key."
)
COMMAND_FAILED_TEXT = f"⚠️ The command failed. Please try again. Details: {LOG_PATH}"
UNEXPECTED_ERROR_TEXT = f"⚠️ Unexpected error. Details were written to {LOG_PATH}"

app = typer.Typer()
logger = logging.getLogger(__name__)


@app.command()
def main() -> None:
    _configure_logging()
    console = Console(theme=rich_theme)
    try:
        _run(console)
    except ConfigError as error:
        console.print(f"⚠️ {error}", style="error")
        raise typer.Exit(code=1) from None
    except openai.OpenAIError:
        logger.exception("Could not start")
        console.print(STARTUP_CONNECTION_ERROR_TEXT, style="error")
        raise typer.Exit(code=1) from None
    except Exception:
        logger.exception("Unexpected error")
        console.print(UNEXPECTED_ERROR_TEXT, style="error")
        raise typer.Exit(code=1) from None


def _run(console: Console) -> None:
    settings = get_settings()
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
        try:
            user_input = prompt(
                HTML("<user-prompt>You ❯ </user-prompt>"),
                completer=slash_completer,
                complete_while_typing=True,
                style=prompt_style,
            )
        except KeyboardInterrupt:
            continue
        except EOFError:
            exit_command(session)
            continue

        command_name = user_input.strip().lower()
        if not command_name:
            continue

        command = COMMANDS.get(command_name)
        if command is not None:
            try:
                command(session)
            except openai.OpenAIError:
                logger.exception("Command %s failed", command_name)
                console.print(COMMAND_FAILED_TEXT, style="error")
            continue

        console.print(build_message_panel(user_input))
        session.conversation = handle_chat_message(
            user_input, session.conversation, chat_service, console
        )


def _configure_logging() -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=LOG_PATH,
        level=logging.WARNING,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


if __name__ == "__main__":
    app()
