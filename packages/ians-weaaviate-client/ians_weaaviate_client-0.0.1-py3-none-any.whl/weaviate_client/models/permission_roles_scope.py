from enum import Enum


class PermissionRolesScope(str, Enum):
    ALL = "all"
    MATCH = "match"

    def __str__(self) -> str:
        return str(self.value)
