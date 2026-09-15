import os
import typer
import re
from dotenv import load_dotenv
from openai import OpenAI
from rich.console import Console
from rich.theme import Theme
from rich.panel import Panel
from rich.table import Table
from database import init_db, save_conversations, get_all_conversations, delete_all_conversations, show_conversation, get_latest_conversations

load_dotenv()

app = typer.Typer()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
conversation = client.conversations.create()

custom_theme = Theme({
    "prompt": "bold cyan",
    "loading": "chartreuse2",
    "input": "bold magenta",
    "output": "bold red",
    "info": "bold yellow",
    "column": "green_yellow",
    "row": "bold slate_blue1",
    "title": "bold medium_orchid1"
})

console = Console(theme=custom_theme)


@app.command()
def main():
    init_db()
    global conversation
    messages = []

    while True:
        user_input = console.input(
            "[prompt]You ❯ [/prompt]")

        # ---- Exit form chat
        if user_input.strip().lower() == "/exit":
            console.print("[info]Goodbye![/info]")
            break

        if not user_input.strip():
            continue

        # ---- Create new chat
        if user_input.strip().lower() == "/new":
            messages = []
            conversation = client.conversations.create()
            console.clear()
            console.print(
                "\n[info]System Chat history cleared. Starting a fresh conversation![/info]")
            continue

        # ---- Show a list of conversations:
        if user_input.strip().lower() == "/resume":
            all_chats = get_all_conversations()
            if all_chats:
                table = Table(
                    title="[title]List of Conversations[/title]", title_justify="left")
                table.add_column(
                    "[column]Number[/column]", justify="left")
                table.add_column(
                    "[column]Conversation ID[/column]", justify="left")

                for i, row in enumerate(all_chats):
                    chat_id = row[0]
                    table.add_row(f"[cyan]{i+1}[/cyan]",
                                  f"[row]{chat_id}[/row]")

                console.print(table)
            else:
                console.print(
                    "[info]💬 This conversation is empty. Type a message to get started![/info]")
            continue
        # ---- Show a 10 latest conversations:
        if user_input.strip().lower() == "/latest":
            latest_chat = get_latest_conversations(10)
            if latest_chat:
                table = Table(
                    title="[title]Top 10 Latest Conversations[/title]", title_justify="left")
                table.add_column(
                    "[column]Number[/column]", justify="left")
                table.add_column(
                    "[column]Conversation ID[/column]", justify="left")

                for i, row in enumerate(latest_chat):
                    chat_id = row[0]
                    table.add_row(f"[cyan]{i+1}[/cyan]",
                                  f"[row]{chat_id}[/row]")

                console.print(table)
            else:
                console.print(
                    "[info]💬 This conversation is empty. Type a message to get started![/info]")
            continue

            # ---- Retrieve conversations from sql database based on conversation id
        id_regex = r"^conv_[0-9a-fA-F]{48}$"

        if re.match(id_regex, user_input.strip()):
            chat_log = show_conversation(user_input.strip())
            table = Table(
                title="[title]Conversation Detail[/title]", title_justify="left")
            table.add_column(
                "[column]Role[/column]", justify="left")
            table.add_column(
                "[column]Content ID[/column]", justify="left")
            table.add_column(
                "[column]Timestamp ID[/column]", justify="left")
            for i, chat in enumerate(chat_log):
                if i % 2 == 0:
                    role_style = f"[output]{chat[2]}[/output]"
                    content_style = f"[output]{chat[3]}[/output]"
                    time_style = f"[output]{chat[4]}[/output]"
                else:
                    role_style = f"[input]{chat[2]}[/input]"
                    content_style = f"[input]{chat[3]}[/input]"
                    time_style = f"[input]{chat[4]}[/input]"
                table.add_row(role_style, content_style, time_style)

            console.print(table)
            continue

        # ---- Delete all of conversations:
        if user_input.strip().lower() == "/delete":
            delete_all_conversations()
            console.print(
                "[info]💥 All conversations have been permanently deleted![/info]")

            continue

        save_conversations(conversation.id, "user", user_input)

        combined_input_text = f"[input]{user_input}[/input]"
        console.print(Panel(combined_input_text, title="[input]User[/input]",
                            border_style="input"))

        messages.append({"role": "user", "content": user_input})

        with console.status("[loading]Thinking... [/loading]"):
            response = client.responses.create(
                model="gpt-6-astra",
                input=[{"role": "user", "content": user_input}],
                conversation=conversation.id
            )
        chat_output = response.output_text

        save_conversations(conversation.id, "assistant", chat_output)

        combined_output_text = f"[output]{chat_output}[/output]"
        console.print(Panel(combined_output_text,
                            title="[output]ChatGPT[/output]", border_style="output"))


if __name__ == "__main__":
    app()
