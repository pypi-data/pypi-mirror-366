from enum import Enum


class BackupRestoreResponseStatus(str, Enum):
    CANCELED = "CANCELED"
    FAILED = "FAILED"
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    TRANSFERRED = "TRANSFERRED"
    TRANSFERRING = "TRANSFERRING"

    def __str__(self) -> str:
        return str(self.value)
