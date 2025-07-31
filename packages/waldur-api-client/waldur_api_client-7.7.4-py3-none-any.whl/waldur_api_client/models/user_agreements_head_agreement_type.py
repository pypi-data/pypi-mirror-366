from enum import Enum


class UserAgreementsHeadAgreementType(str, Enum):
    PP = "PP"
    TOS = "TOS"

    def __str__(self) -> str:
        return str(self.value)
