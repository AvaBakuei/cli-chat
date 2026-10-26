"""Talks to the OpenAI API. Knows nothing about the terminal or the database."""

import time
import logging
import openai
from typing import Any

from openai import OpenAI
from openai.types.conversations import Conversation
from openai.types.responses import Response

TITLE_INSTRUCTIONS = (
    "You are a utility that generates short titles for chat logs. "
    "Summarize the user's request in 3 to 5 words. "
    "Do not use quotes, punctuation, or prefix words like 'Title:'."
)
PENDING_STATUSES = {"queued", "in_progress"}
POLL_INTERVAL_SECONDS = 0.2
logger = logging.getLogger(__name__)


class ChatServiceError(Exception):
    """The API finished a request without a usable answer."""


class ChatService:
    def __init__(self, client: OpenAI, model: str) -> None:
        self._client = client
        self._model = model
        self._active_response_id: str | None = None

    def start_conversation(self) -> Conversation:
        return self._client.conversations.create()

    def get_conversation(self, conversation_id: str) -> Conversation:
        return self._client.conversations.retrieve(conversation_id)

    def generate_title(self, user_input: str) -> str:
        response = self._run_in_background(
            instructions=TITLE_INSTRUCTIONS,
            input=[{"role": "user", "content": user_input}],
        )
        return response.output_text

    def update_title(self, conversation_id: str, title: str) -> Conversation:
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

    def cancel_active_request(self) -> None:
        if self._active_response_id is None:
            return
        try:
            self._client.with_options(max_retries=0).responses.cancel(self._active_response_id)
        except openai.OpenAIError:  # ← only OpenAI errors
            logger.warning(  # ← write it down
                "Could not cancel response %s", self._active_response_id, exc_info=True
            )
        finally:
            self._active_response_id = None

    def _run_in_background(self, **request: Any) -> Response:
        response = self._client.responses.create(model=self._model, background=True, **request)
        self._active_response_id = response.id
        while response.status in PENDING_STATUSES:
            time.sleep(POLL_INTERVAL_SECONDS)
            response = self._client.responses.retrieve(response.id)
        self._active_response_id = None
        if response.status != "completed":
            raise ChatServiceError(f"Response {response.id} ended with status {response.status!r}")
        return response
