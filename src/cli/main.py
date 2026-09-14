import typer
import os
from dotenv import load_dotenv
from openai import OpenAI
from rich.console import Console
from rich.padding import Padding
from rich.theme import Theme
from rich.panel import Panel


app = typer.Typer()

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

custom_theme = Theme({
    "input": "bold magenta",
    "output": "bold red",
    "info": "bold yellow"
})
console = Console(theme=custom_theme)


@app.command()
def main():
    while True:
        console.print(
            ":backhand_index_pointing_right: ", end="")
        user_input = input()

        if user_input.strip().lower() == "/exit":
            console.print("[info]Goodbye![/info]")
            break

        combined_input_text = f"[input]{user_input}[/input]"
        console.print(Panel(combined_input_text, title="[input]User[/input]",
                            border_style="input"))

        response = client.responses.create(
            model="gpt-6-astra",
            input=user_input,
        )
        chat_output = response.output_text

        combined_output_text = f"[output]{chat_output}[/output]"
        console.print(Panel(combined_output_text,
                            title="[output]ChatGPT[/output]", border_style="output"))


if __name__ == "__main__":
    app()
