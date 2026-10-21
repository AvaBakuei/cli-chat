"""Pagination and selection state for the /resume list. Contains no terminal code."""
from cli_chat.models import ConversationSummary

BACK_ROW = 0


class ConversationPicker:
    def __init__(self, conversations: list[ConversationSummary], items_per_page: int) -> None:
        self._conversations = conversations
        self.items_per_page = items_per_page
        self.page = 0
        self.selected_row = 1

    @property
    def page_items(self) -> list[ConversationSummary]:
        start = self.page * self.items_per_page
        return self._conversations[start:start + self.items_per_page]

    @property
    def has_back(self) -> bool:
        return self.page > 0

    @property
    def has_more(self) -> bool:
        return (self.page + 1) * self.items_per_page < len(self._conversations)

    @property
    def _more_row(self) -> int:
        return len(self.page_items) + 1

    def move_up(self) -> None:
        self.selected_row = max(BACK_ROW, self.selected_row - 1)

    def move_down(self) -> None:
        self.selected_row = min(self._more_row, self.selected_row + 1)

    def press_enter(self) -> ConversationSummary | None:
        """Change the page, or return the chosen conversation."""
        if self.selected_row == BACK_ROW and self.has_back:
            self.page -= 1
            self.selected_row = self.items_per_page
        elif self.selected_row == self._more_row and self.has_more:
            self.page += 1
            self.selected_row = 1
        elif 1 <= self.selected_row <= len(self.page_items):
            return self.page_items[self.selected_row - 1]
        return None
