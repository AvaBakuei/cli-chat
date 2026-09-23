import time
import threading
import os
from dotenv import load_dotenv
from openai import OpenAI
from readchar import readkey
from cli.LocalRepository import save_conversations
from layer.ui.display import conversation_disply


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

active_responses = set()
cancel_event = threading.Event()


def cancel_all_responses(console):
    cancel_event.set()
    for response_id in list(active_responses):
        try:
            client.responses.cancel(response_id, max_retries=0)
        except Exception:
            pass
    console.print("[red]❌ Process canceled by user.[/red]")


def listen_for_cancel(console):
    key = readkey()
    if key.lower() == "c":
        cancel_all_responses(console)


def openai_api(user_input, conversation, console):
    is_first_turn_of_chat = "title" not in conversation.metadata

    cancel_event.clear()

    cancel_listener = threading.Thread(
        target=listen_for_cancel,
        args=(console,),
        daemon=True
    )
    cancel_listener.start()

    with console.status("[loading]Thinking...[/loading]     \n\n[dim]💡 Press [bold][C][/bold] to cancel[/dim]") as status:
        if is_first_turn_of_chat:

            title_response = client.responses.create(
                model="gpt-6-astra",
                instructions="You are a utility that generates short titles for chat logs. Summarize the user's request in 3 to 5 words. Do not use quotes, punctuation, or prefix words like 'Title:'.",
                input=[{"role": "user", "content": user_input}],
                background=True,
            )

            active_responses.add(title_response.id)

            while title_response.status in {
                "queued",
                "in_progress"
            }:

                if cancel_event.is_set():
                    active_responses.discard(title_response.id)
                    return

                time.sleep(0.2)

                title_response = client.responses.retrieve(title_response.id)

            active_responses.discard(title_response.id)

            if cancel_event.is_set():
                return

            client_title = title_response.output_text

            conversation = client.conversations.update(
                conversation_id=conversation.id,
                metadata={"title": client_title}
            )

        save_conversations(
            conversation.id, client_title, "user", user_input, conversation.created_at)

        response = client.responses.create(
            model="gpt-6-astra",
            input=[{"role": "user", "content": user_input}],
            conversation=conversation.id,
            background=True
        )

        while response.status in {
            "queued",
            "in_progress"
        }:
            if cancel_event.is_set():
                active_responses.discard(response.id)
                return

            time.sleep(0.2)

            response = client.responses.retrieve(
                response.id
            )

        active_responses.discard(response.id)

        if cancel_event.is_set():
            return

        chat_output = response.output_text

        save_conversations(conversation.id, client_title,
                           "assistant", chat_output, conversation.created_at)
        chat_conversation = conversation_disply(
            chat_output, console, is_user=False)
        console.print(chat_conversation)
