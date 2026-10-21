import sys

from readchar import key, readkey
from rich.live import Live

from cli_chat.commands.resume_picker import ConversationPicker
from cli_chat.models import ConversationSummary
from cli_chat.storage.conversation_repository import (
    delete_all_conversations,
    get_messages,
    list_conversations,
)
from cli_chat.ui.conversation_table import build_conversation_table
from cli_chat.ui.history import build_history_view


def handle_new_command(user_input, console):
    if user_input.strip().lower() != "/new":
        return False
    console.clear()
    console.print(
        "\nSystem Chat history cleared. Starting a fresh conversation!", style="info")
    return True


def handle_resume_command(user_input, console, items_per_page, result_data):
    if user_input.strip().lower() != "/resume":
        return False
    conversations = list_conversations()
    if not conversations:
        console.print(
            "💬 This conversation is empty. Type a message to get started!", style="info")
        return True

    picker = ConversationPicker(conversations, items_per_page)
    selected = _choose_conversation(picker, console)

    messages = get_messages(selected.conversation_id)
    console.print(build_history_view(messages))
    result_data["selected_chat"] = selected.conversation_id
    return True


def handle_delete_command(user_input, console):
    if user_input.strip().lower() != "/delete":
        return False
    delete_all_conversations()
    console.print(
        "💥 All conversations have been permanently deleted!", style="info")
    return True


def handle_exit_command(user_input, console):
    if user_input.strip().lower() != "/exit":
        return False
    console.print("Goodbye!", style="info")
    return True


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
