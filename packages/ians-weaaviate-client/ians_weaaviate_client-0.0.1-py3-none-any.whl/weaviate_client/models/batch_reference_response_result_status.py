from enum import Enum


class BatchReferenceResponseResultStatus(str, Enum):
    FAILED = "FAILED"
    SUCCESS = "SUCCESS"

    def __str__(self) -> str:
        return str(self.value)
