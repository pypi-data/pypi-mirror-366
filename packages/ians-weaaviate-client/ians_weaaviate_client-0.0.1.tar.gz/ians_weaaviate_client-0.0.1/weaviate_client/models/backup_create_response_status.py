from enum import Enum


class BackupCreateResponseStatus(str, Enum):
    CANCELED = "CANCELED"
    FAILED = "FAILED"
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    TRANSFERRED = "TRANSFERRED"
    TRANSFERRING = "TRANSFERRING"

    def __str__(self) -> str:
        return str(self.value)
