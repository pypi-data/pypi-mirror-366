from enum import Enum


class GetRolesForUserUserType(str, Enum):
    DB = "db"
    OIDC = "oidc"

    def __str__(self) -> str:
        return str(self.value)
