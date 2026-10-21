from rich.panel import Panel
from rich.text import Text


def build_message_panel(text: str, is_user: bool = True) -> Panel:
    style, label = ("input", "User") if is_user else ("output", "ChatGPT")
    return Panel(Text(text, style=style), title=Text(label, style=style), border_style=style)
