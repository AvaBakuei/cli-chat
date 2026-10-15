from rich.console import Group
from cli.conversation_repository import get_messages
from layer.ui.panels import build_message_panel


def build_history_view(selected_conversation):
    chat_log = get_messages(selected_conversation[2])
    panels = []

    for chat in chat_log:
        _, _, _, role, content, _ = chat

        is_user = (role.lower() == "user")
        panel = build_message_panel(content, is_user=is_user)
        panels.append(panel)
    return Group(*panels)
