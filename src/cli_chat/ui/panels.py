from rich.panel import Panel
from rich.text import Text


def build_message_panel(text: str, is_user: bool = True) -> Panel:
    if is_user:
        return Panel(Text(text, style="input"), title="[input]User[/input]", border_style="input")
    return Panel(Text(text, style="output"), title="[output]ChatGPT[/output]", border_style="output")
