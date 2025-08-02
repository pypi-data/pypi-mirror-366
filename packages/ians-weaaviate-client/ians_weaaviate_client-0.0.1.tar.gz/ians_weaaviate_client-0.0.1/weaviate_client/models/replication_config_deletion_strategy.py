from enum import Enum


class ReplicationConfigDeletionStrategy(str, Enum):
    DELETEONCONFLICT = "DeleteOnConflict"
    NOAUTOMATEDRESOLUTION = "NoAutomatedResolution"
    TIMEBASEDRESOLUTION = "TimeBasedResolution"

    def __str__(self) -> str:
        return str(self.value)
