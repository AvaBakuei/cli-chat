import sys
from rich.live import Live
from readchar import readkey, key
from layer.ui.table import draw_table
from layer.ui.chat import get_chat_history
from cli.LocalRepository import get_all_conversations, delete_all_conversations


def handle_new_command(user_input, console):
    if user_input.strip().lower() != "/new":
        return False
    console.clear()
    console.print(
        "\n[info]System Chat history cleared. Starting a fresh conversation![/info]")
    return True


def hanlde_resume_command(user_input, console, ITEMS_PER_PAGE, current_page, current_selection, all_chats):
    if user_input.strip().lower() != "/resume":
        return False
    all_chats = get_all_conversations()
    if not all_chats:
        console.print(
            "[info]💬 This conversation is empty. Type a message to get started![/info]")
        return True

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
                    chat_history_group = get_chat_history(selected_chat)
                    console.print(chat_history_group)
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
