from enum import Enum


class UserTypeOutput(str, Enum):
    DB_ENV_USER = "db_env_user"
    DB_USER = "db_user"
    OIDC = "oidc"

    def __str__(self) -> str:
        return str(self.value)
