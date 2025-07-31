from enum import Enum


class BroadcastMessagesHeadState(str, Enum):
    DRAFT = "DRAFT"
    SCHEDULED = "SCHEDULED"
    SENT = "SENT"

    def __str__(self) -> str:
        return str(self.value)
