from rich.console import Group
from src.cli.LocalRepository import show_conversation
from layer.ui.display import conversation_disply


def get_chat_history(selected_conversation):
    # ---- Retrieve conversations from sql database based on conversation id
    chat_log = show_conversation(selected_conversation[2])
    panels = []

    for chat in chat_log:
        msg_id, conv_id, title, role, content, created_at = chat

        is_user = (role.lower() == "user")
        panel = conversation_disply(content, console=None, is_user=is_user)
        panels.append(panel)
    return Group(*panels)
