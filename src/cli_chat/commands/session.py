"""Everything a command needs, bundled in one object."""

from dataclasses import dataclass

from openai.types.conversations import Conversation
from rich.console import Console

from cli_chat.config import Settings
from cli_chat.services.chat_service import ChatService


@dataclass
class Session:
    console: Console
    chat_service: ChatService
    settings: Settings
    conversation: Conversation
    is_running: bool = True
