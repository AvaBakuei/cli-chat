"""Slash commands. Every command receives the session and may change it."""

import sys
from collections.abc import Callable

from readchar import key, readkey
from rich.live import Live

from cli_chat.commands.resume_picker import ConversationPicker
from cli_chat.commands.session import Session
from cli_chat.models import ConversationSummary
from cli_chat.storage.conversation_repository import (
    delete_all_conversations,
    get_messages,
    list_conversations,
)
from cli_chat.ui.conversation_table import build_conversation_table
from cli_chat.ui.history import build_history_view


def new_command(session: Session) -> None:
    session.console.clear()
    session.console.print(
        "\nStarted a new conversation. Previous chats are available with /resume.",
        style="info",
    )
    session.conversation = session.chat_service.start_conversation()


def resume_command(session: Session) -> None:
    conversations = list_conversations()
    if not conversations:
        session.console.print(
            "💬 This conversation is empty. Type a message to get started!", style="info"
        )
        return

    picker = ConversationPicker(conversations, session.settings.items_per_page)
    selected = _choose_conversation(picker, session.console)

    session.console.print(build_history_view(get_messages(selected.conversation_id)))
    session.conversation = session.chat_service.get_conversation(selected.conversation_id)


def delete_command(session: Session) -> None:
    delete_all_conversations()
    session.console.print("💥 All conversations have been permanently deleted!", style="info")


def exit_command(session: Session) -> None:
    session.console.print("Goodbye!", style="info")
    session.is_running = False


COMMANDS: dict[str, Callable[[Session], None]] = {
    "/new": new_command,
    "/resume": resume_command,
    "/delete": delete_command,
    "/exit": exit_command,
}


def _choose_conversation(picker: ConversationPicker, console) -> ConversationSummary:
    with Live(_render(picker), console=console, auto_refresh=False, transient=True) as live:
        while True:
            pressed = readkey()
            if pressed == key.UP:
                picker.move_up()
            elif pressed == key.DOWN:
                picker.move_down()
            elif pressed == key.ENTER:
                selected = picker.press_enter()
                if selected is not None:
                    return selected
            elif pressed == key.CTRL_C:
                sys.exit(0)
            live.update(_render(picker), refresh=True)


def _render(picker: ConversationPicker):
    return build_conversation_table(
        picker.selected_row,
        picker.page_items,
        picker.has_back,
        picker.has_more,
        page=picker.page,
        items_per_page=picker.items_per_page,
    )
