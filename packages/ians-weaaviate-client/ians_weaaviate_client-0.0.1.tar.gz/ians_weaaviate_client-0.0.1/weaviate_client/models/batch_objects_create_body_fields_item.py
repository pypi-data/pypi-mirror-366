from enum import Enum


class BatchObjectsCreateBodyFieldsItem(str, Enum):
    ALL = "ALL"
    CLASS = "class"
    CREATIONTIMEUNIX = "creationTimeUnix"
    ID = "id"
    SCHEMA = "schema"

    def __str__(self) -> str:
        return str(self.value)
