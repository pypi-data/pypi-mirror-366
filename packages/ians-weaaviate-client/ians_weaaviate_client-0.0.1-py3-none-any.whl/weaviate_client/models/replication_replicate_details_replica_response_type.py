from enum import Enum


class ReplicationReplicateDetailsReplicaResponseType(str, Enum):
    COPY = "COPY"
    MOVE = "MOVE"

    def __str__(self) -> str:
        return str(self.value)
