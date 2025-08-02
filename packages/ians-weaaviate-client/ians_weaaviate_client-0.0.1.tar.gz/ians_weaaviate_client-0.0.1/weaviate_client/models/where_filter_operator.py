from enum import Enum


class WhereFilterOperator(str, Enum):
    AND = "And"
    CONTAINSALL = "ContainsAll"
    CONTAINSANY = "ContainsAny"
    EQUAL = "Equal"
    GREATERTHAN = "GreaterThan"
    GREATERTHANEQUAL = "GreaterThanEqual"
    ISNULL = "IsNull"
    LESSTHAN = "LessThan"
    LESSTHANEQUAL = "LessThanEqual"
    LIKE = "Like"
    NOTEQUAL = "NotEqual"
    OR = "Or"
    WITHINGEORANGE = "WithinGeoRange"

    def __str__(self) -> str:
        return str(self.value)
