import os
import typer
from dotenv import load_dotenv
from openai import OpenAI
from rich.console import Console
from layer.ui.theme import custom_theme
from cli.LocalRepository import init_db
from layer.command import handle_new_command, hanlde_resume_command, handle_delete_command, handle_exit_command
from layer.ui.display import conversation_disply
from cli.remoteRepository import openai_api

load_dotenv()

app = typer.Typer()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
conversation = client.conversations.create()


console = Console(theme=custom_theme)


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
        if hanlde_resume_command(user_input, console, ITEMS_PER_PAGE, current_page, current_selection, all_chats):
            continue

        # ---- Delete all of conversations:
        if handle_delete_command(user_input, console):
            continue

        conversation_disply(user_input, console)

        openai_api(user_input, conversation, console)


if __name__ == "__main__":
    app()
