"""Talks to the OpenAI API. Knows nothing about the terminal or the database."""
import threading
import time

from openai import OpenAI

TITLE_INSTRUCTIONS = (
    "You are a utility that generates short titles for chat logs. "
    "Summarize the user's request in 3 to 5 words. "
    "Do not use quotes, punctuation, or prefix words like 'Title:'."
)
PENDING_STATUSES = {"queued", "in_progress"}
POLL_INTERVAL_SECONDS = 0.2


class RequestCancelled(Exception):
    """Raised when the user cancels a running request."""


class ChatService:
    def __init__(self, client: OpenAI, model: str) -> None:
        self._client = client
        self._model = model
        self._active_response_ids: set[str] = set()
        self._cancel_event = threading.Event()

    def start_conversation(self):
        return self._client.conversations.create()

    def get_conversation(self, conversation_id: str):
        return self._client.conversations.retrieve(conversation_id)

    def generate_title(self, user_input: str) -> str:
        response = self._run_in_background(
            instructions=TITLE_INSTRUCTIONS,
            input=[{"role": "user", "content": user_input}],
        )
        return response.output_text

    def update_title(self, conversation_id: str, title: str):
        return self._client.conversations.update(
            conversation_id=conversation_id,
            metadata={"title": title},
        )

    def ask(self, user_input: str, conversation_id: str) -> str:
        response = self._run_in_background(
            input=[{"role": "user", "content": user_input}],
            conversation=conversation_id,
        )
        return response.output_text

    def reset_cancellation(self) -> None:
        self._cancel_event.clear()

    def cancel(self) -> None:
        self._cancel_event.set()
        for response_id in list(self._active_response_ids):
            try:
                self._client.responses.cancel(response_id, max_retries=0)
            except Exception:
                pass  # unchanged behaviour – error handling is step 11

    def _run_in_background(self, **request):
        response = self._client.responses.create(
            model=self._model, background=True, **request
        )
        self._active_response_ids.add(response.id)
        try:
            while response.status in PENDING_STATUSES:
                if self._cancel_event.is_set():
                    raise RequestCancelled
                time.sleep(POLL_INTERVAL_SECONDS)
                response = self._client.responses.retrieve(response.id)
        finally:
            self._active_response_ids.discard(response.id)

        if self._cancel_event.is_set():
            raise RequestCancelled
        return response
