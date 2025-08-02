from enum import Enum


class ReplicationReplicateDetailsReplicaStatusState(str, Enum):
    CANCELLED = "CANCELLED"
    DEHYDRATING = "DEHYDRATING"
    FINALIZING = "FINALIZING"
    HYDRATING = "HYDRATING"
    READY = "READY"
    REGISTERED = "REGISTERED"

    def __str__(self) -> str:
        return str(self.value)
