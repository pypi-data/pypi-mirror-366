from enum import Enum


class BatchDeleteResponseResultsObjectsItemStatus(str, Enum):
    DRYRUN = "DRYRUN"
    FAILED = "FAILED"
    SUCCESS = "SUCCESS"

    def __str__(self) -> str:
        return str(self.value)
