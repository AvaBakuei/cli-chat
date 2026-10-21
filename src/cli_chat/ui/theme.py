from prompt_toolkit.styles import Style
from rich.theme import Theme

rich_theme = Theme({
    "loading": "chartreuse2",
    "input": "bold magenta",
    "output": "bold red",
    "info": "bold yellow",
    "error": "red",
    "column": "green_yellow",
    "row": "bold slate_blue1",
    "selected_row": "bold slate_blue1 on dark_olive_green1",
    "title": "bold medium_orchid1",
})


prompt_style = Style.from_dict({
    "user-prompt": "fg:cyan bold",
    "completion-menu": "bg:#2a2a2a fg:#dcdcdc",
    "completion-menu.completion.current": "bg:#A178DF fg:#ffffff bold",
    "completion-menu.completion": "fg:#a0a0a0",
})
