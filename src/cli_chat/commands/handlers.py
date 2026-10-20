import sys
from rich.live import Live
from readchar import readkey, key
from cli_chat.ui.conversation_table import build_conversation_table
from cli_chat.ui.history import build_history_view
from cli_chat.storage.conversation_repository import (
    delete_all_conversations,
    get_messages,
    list_conversations,
)


def handle_new_command(user_input, console):
    if user_input.strip().lower() != "/new":
        return False
    console.clear()
    console.print(
        "\n[info]System Chat history cleared. Starting a fresh conversation![/info]")
    return True


def handle_resume_command(user_input, console, items_per_page, current_page, current_selection, all_chats, result_data):
    if user_input.strip().lower() != "/resume":
        return False
    all_chats = list_conversations()
    if not all_chats:
        console.print(
            "[info]💬 This conversation is empty. Type a message to get started![/info]")
        return True

    with Live(build_conversation_table([], []), console=console, auto_refresh=False, transient=True) as live:
        while True:
            start_index = current_page * items_per_page
            end_index = start_index + items_per_page

            page_data = all_chats[start_index:end_index]

            has_back = current_page > 0
            has_more = end_index < len(all_chats)

            live.update(build_conversation_table(current_selection,
                                   page_data, has_back, has_more, page=current_page, items_per_page=items_per_page), refresh=True)

            pressed = readkey()
            if pressed == key.UP:
                current_selection = max(0, current_selection - 1)
            elif pressed == key.DOWN:
                current_selection = min(
                    len(page_data) + 1, current_selection + 1)
            elif pressed == key.ENTER:
                if current_selection == 0 and has_back:
                    current_page -= 1
                    current_selection = items_per_page
                elif current_selection == len(page_data) + 1 and has_more:
                    current_page += 1
                    current_selection = 1
                elif 1 <= current_selection <= len(page_data):
                    actual_chat_index = start_index + \
                        (current_selection - 1)
                    selected = all_chats[actual_chat_index]
                    messages = get_messages(selected.conversation_id)
                    console.print(build_history_view(messages))
                    result_data["selected_chat"] = selected.conversation_id
                    break

            elif pressed == key.CTRL_C:
                sys.exit(0)

        return True


def handle_delete_command(user_input, console):
    if user_input.strip().lower() != "/delete":
        return False
    delete_all_conversations()
    console.print(
        "[info]💥 All conversations have been permanently deleted![/info]")
    return True


def handle_exit_command(user_input, console):
    if user_input.strip().lower() != "/exit":
        return False
    console.print("[info]Goodbye![/info]")
    return True
