from rich.panel import Panel


def conversation_disply(text, console, is_user=True):
    if is_user:
        combined_input_text = f"[input]{text}[/input]"
        panel = Panel(combined_input_text, title="[input]User[/input]",
                      border_style="input")
    else:
        combined_output_text = f"[output]{text}[/output]"
        panel = Panel(combined_output_text,
                      title="[output]ChatGPT[/output]", border_style="output")

    return panel
