import os
import typer
from dotenv import load_dotenv
from openai import OpenAI
from rich.console import Console
from rich.theme import Theme
from rich.panel import Panel
from time import sleep

load_dotenv()

app = typer.Typer()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
conversation = client.conversations.create()

custom_theme = Theme({
    "prompt": "bold cyan",
    "loading": "chartreuse2",
    "input": "bold magenta",
    "output": "bold red",
    "info": "bold yellow"
})
console = Console(theme=custom_theme)


@app.command()
def main():
    console.print(
        f"[info]Started conversation session: {conversation.id}[/info]\n")

    while True:

        user_input = console.input(
            "[prompt]You ❯ [/prompt]")

        if user_input.strip().lower() == "/exit":
            console.print("[info]Goodbye![/info]")
            break

        if not user_input.strip():
            continue

        combined_input_text = f"[input]{user_input}[/input]"
        console.print(Panel(combined_input_text, title="[input]User[/input]",
                            border_style="input"))
        with console.status("[loading]Thinking... [/loading]"):
            response = client.responses.create(
                model="gpt-6-astra",
                input=[{"role": "user", "content": user_input}],
                conversation=conversation.id
            )
        chat_output = response.output_text

        combined_output_text = f"[output]{chat_output}[/output]"
        console.print(Panel(combined_output_text,
                            title="[output]ChatGPT[/output]", border_style="output"))


if __name__ == "__main__":
    app()
