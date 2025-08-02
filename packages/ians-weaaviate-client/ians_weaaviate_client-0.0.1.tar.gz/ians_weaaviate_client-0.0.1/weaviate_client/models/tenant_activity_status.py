from enum import Enum


class TenantActivityStatus(str, Enum):
    ACTIVE = "ACTIVE"
    COLD = "COLD"
    FREEZING = "FREEZING"
    FROZEN = "FROZEN"
    HOT = "HOT"
    INACTIVE = "INACTIVE"
    OFFLOADED = "OFFLOADED"
    OFFLOADING = "OFFLOADING"
    ONLOADING = "ONLOADING"
    UNFREEZING = "UNFREEZING"

    def __str__(self) -> str:
        return str(self.value)
