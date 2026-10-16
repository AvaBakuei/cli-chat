"""Plain data objects shared between layers."""

from dataclasses import dataclass

@dataclass(frozen=True)
class Message:
    conversation_id: str
    role: str
    content: str
    timestamp: int

    @property
    def is_user(self) -> bool:
        return self.role.lower() == "user"

@dataclass(frozen=True)
class ConversationSummary:
    conversation_id: str
    title: str
    last_activity: int

