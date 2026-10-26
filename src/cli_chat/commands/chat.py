"""Handles a normal chat message: ask the model, store both sides, show the answer."""

import logging

import openai
from openai.types.conversations import Conversation
from rich.console import Console

from cli_chat.config import LOG_PATH
from cli_chat.services.chat_service import ChatService, ChatServiceError
from cli_chat.storage.conversation_repository import save_message
from cli_chat.ui.panels import build_message_panel

THINKING_STATUS = (
    "[loading]Thinking...[/loading]     \n\n[dim]💡 Press [bold]Ctrl+C[/bold] to cancel[/dim]"
)
CANCELLED_TEXT = "❌ Process canceled by user."
AUTH_ERROR_TEXT = "⚠️ OpenAI rejected the API key. Check OPENAI_API_KEY in your .env file."
CONNECTION_ERROR_TEXT = "⚠️ Could not reach OpenAI. Check your internet connection and try again."
REQUEST_FAILED_TEXT = f"⚠️ The request failed. Please try again. Details: {LOG_PATH}"

logger = logging.getLogger(__name__)


def handle_chat_message(
    user_input: str,
    conversation: Conversation,
    chat_service: ChatService,
    console: Console,
) -> Conversation:
    """Send one message and return the (possibly updated) conversation."""
    try:
        with console.status(THINKING_STATUS):
            title = _title_of(conversation)
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
    except openai.AuthenticationError:
        logger.exception("Authentication failed")
        console.print(AUTH_ERROR_TEXT, style="error")
        return conversation
    except openai.APIConnectionError:
        logger.exception("Could not connect to OpenAI")
        console.print(CONNECTION_ERROR_TEXT, style="error")
        return conversation
    except (openai.OpenAIError, ChatServiceError):
        logger.exception("Chat request failed")
        console.print(REQUEST_FAILED_TEXT, style="error")
        return conversation

    console.print(build_message_panel(answer_text, is_user=False))
    return conversation


def _title_of(conversation: Conversation) -> str | None:
    metadata = conversation.metadata
    if isinstance(metadata, dict):
        return metadata.get("title")
    return None
