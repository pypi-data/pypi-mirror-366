from enum import Enum


class ChecklistTypeEnum(str, Enum):
    OFFERING_COMPLIANCE = "offering_compliance"
    PROJECT_COMPLIANCE = "project_compliance"
    PROPOSAL_COMPLIANCE = "proposal_compliance"

    def __str__(self) -> str:
        return str(self.value)
