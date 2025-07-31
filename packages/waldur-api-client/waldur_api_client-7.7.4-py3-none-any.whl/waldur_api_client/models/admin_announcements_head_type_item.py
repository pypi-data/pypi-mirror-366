from enum import Enum


class AdminAnnouncementsHeadTypeItem(str, Enum):
    DANGER = "danger"
    INFORMATION = "information"
    WARNING = "warning"

    def __str__(self) -> str:
        return str(self.value)
