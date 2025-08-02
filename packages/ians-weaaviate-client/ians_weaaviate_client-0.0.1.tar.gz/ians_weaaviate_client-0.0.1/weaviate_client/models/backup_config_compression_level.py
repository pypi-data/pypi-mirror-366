from enum import Enum


class BackupConfigCompressionLevel(str, Enum):
    BESTCOMPRESSION = "BestCompression"
    BESTSPEED = "BestSpeed"
    DEFAULTCOMPRESSION = "DefaultCompression"

    def __str__(self) -> str:
        return str(self.value)
