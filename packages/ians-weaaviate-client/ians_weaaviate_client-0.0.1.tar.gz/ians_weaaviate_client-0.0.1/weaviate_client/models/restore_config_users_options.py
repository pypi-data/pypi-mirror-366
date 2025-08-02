from enum import Enum


class RestoreConfigUsersOptions(str, Enum):
    ALL = "all"
    NORESTORE = "noRestore"

    def __str__(self) -> str:
        return str(self.value)
