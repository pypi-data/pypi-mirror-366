from enum import Enum


class RestoreConfigRolesOptions(str, Enum):
    ALL = "all"
    NORESTORE = "noRestore"

    def __str__(self) -> str:
        return str(self.value)
