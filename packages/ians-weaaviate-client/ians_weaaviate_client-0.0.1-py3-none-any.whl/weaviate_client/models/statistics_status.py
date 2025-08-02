from enum import Enum


class StatisticsStatus(str, Enum):
    HEALTHY = "HEALTHY"
    TIMEOUT = "TIMEOUT"
    UNAVAILABLE = "UNAVAILABLE"
    UNHEALTHY = "UNHEALTHY"

    def __str__(self) -> str:
        return str(self.value)
