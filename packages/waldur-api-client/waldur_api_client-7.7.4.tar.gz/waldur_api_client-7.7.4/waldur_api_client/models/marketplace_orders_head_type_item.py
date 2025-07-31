from enum import Enum


class MarketplaceOrdersHeadTypeItem(str, Enum):
    CREATE = "Create"
    TERMINATE = "Terminate"
    UPDATE = "Update"

    def __str__(self) -> str:
        return str(self.value)
