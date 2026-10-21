from rich.console import Group

from cli_chat.models import Message
from cli_chat.ui.panels import build_message_panel


def build_history_view(messages: list[Message]) -> Group:
    panels = [build_message_panel(msg.content, is_user=msg.is_user) for msg in messages]
    return Group(*panels)
