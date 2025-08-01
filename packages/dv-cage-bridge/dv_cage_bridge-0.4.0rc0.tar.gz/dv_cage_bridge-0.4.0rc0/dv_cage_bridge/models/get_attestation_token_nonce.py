from enum import Enum


class GetAttestationTokenNonce(str, Enum):
    FINGERPRINT = "fingerprint"

    def __str__(self) -> str:
        return str(self.value)
