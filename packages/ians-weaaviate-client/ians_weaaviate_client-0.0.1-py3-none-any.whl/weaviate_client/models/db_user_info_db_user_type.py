from enum import Enum


class DBUserInfoDbUserType(str, Enum):
    DB_ENV_USER = "db_env_user"
    DB_USER = "db_user"

    def __str__(self) -> str:
        return str(self.value)
