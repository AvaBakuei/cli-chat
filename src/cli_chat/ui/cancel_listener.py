"""Listens for the cancel key in the background while a request is running."""
import threading
from collections.abc import Callable

from readchar import readkey

CANCEL_KEY = "c"


def start_cancel_listener(on_cancel: Callable[[], None]) -> None:
    def listen() -> None:
        if readkey().lower() == CANCEL_KEY:
            on_cancel()

    threading.Thread(target=listen, daemon=True).start()
