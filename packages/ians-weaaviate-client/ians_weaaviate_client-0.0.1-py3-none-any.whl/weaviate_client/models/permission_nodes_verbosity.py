from enum import Enum


class PermissionNodesVerbosity(str, Enum):
    MINIMAL = "minimal"
    VERBOSE = "verbose"

    def __str__(self) -> str:
        return str(self.value)
