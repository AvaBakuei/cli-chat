"""Handles a normal chat message: ask the model, store both sides, show the answer."""

from rich.console import Console

from cli_chat.services.chat_service import ChatService
from cli_chat.storage.conversation_repository import save_message
from cli_chat.ui.panels import build_message_panel

THINKING_STATUS = (
    "[loading]Thinking...[/loading]     \n\n[dim]💡 Press [bold]Ctrl+C[/bold] to cancel[/dim]"
)
CANCELLED_TEXT = "❌ Process canceled by user."


def handle_chat_message(user_input, conversation, chat_service: ChatService, console: Console):
    """Send one message and return the (possibly updated) conversation."""
    try:
        with console.status(THINKING_STATUS):
            title = conversation.metadata.get("title")
            if title is None:
                title = chat_service.generate_title(user_input)
                conversation = chat_service.update_title(conversation.id, title)

            save_message(conversation.id, title, "user", user_input)
            answer_text = chat_service.ask(user_input, conversation.id)
            save_message(conversation.id, title, "assistant", answer_text)
    except KeyboardInterrupt:
        chat_service.cancel_active_request()
        console.print(CANCELLED_TEXT, style="error")
        return conversation

    console.print(build_message_panel(answer_text, is_user=False))
    return conversation
