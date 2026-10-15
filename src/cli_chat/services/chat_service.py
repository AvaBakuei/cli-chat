import time
import threading
from openai import OpenAI
from readchar import readkey
from cli_chat.config import get_settings
from cli_chat.storage.conversation_repository import save_message
from cli_chat.ui.panels import build_message_panel


client = OpenAI(api_key=get_settings().openai_api_key)

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


def send_message(user_input, conversation, console):
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
                model=get_settings().model,
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

            title = title_response.output_text

            conversation = client.conversations.update(
                conversation_id=conversation.id,
                metadata={"title": title}
            )

        save_message(
            conversation.id, title, "user", user_input, conversation.created_at)

        response = client.responses.create(
            model=get_settings().model,
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

        answer_text = response.output_text

        save_message(conversation.id, title,
                           "assistant", answer_text, conversation.created_at)
        chat_conversation = build_message_panel(
            answer_text, is_user=False)
        console.print(chat_conversation)
