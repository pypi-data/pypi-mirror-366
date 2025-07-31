from enum import Enum


class MarketplaceOfferingUsersListStateItem(str, Enum):
    CREATING = "Creating"
    DELETED = "Deleted"
    DELETING = "Deleting"
    ERROR = "Error"
    OK = "OK"
    PENDING_ACCOUNT_LINKING = "Pending account linking"
    PENDING_ADDITIONAL_VALIDATION = "Pending additional validation"
    REQUESTED = "Requested"
    REQUESTED_DELETION = "Requested deletion"

    def __str__(self) -> str:
        return str(self.value)
