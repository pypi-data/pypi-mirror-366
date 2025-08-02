from enum import Enum


class ReplicationReplicateReplicaRequestType(str, Enum):
    COPY = "COPY"
    MOVE = "MOVE"

    def __str__(self) -> str:
        return str(self.value)
