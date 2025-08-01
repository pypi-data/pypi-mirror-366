from enum import Enum


class ShareType(str, Enum):
    AVAILABLE = "AVAILABLE"
    """ The share is available for subscription """
    PUBLISHER = "PUBLISHER"
    """ The project owns this share """
    SUBSCRIBER = "SUBSCRIBER"
    """ The project can view this share """
    UNKNOWN = "UNKNOWN"
    """ This is a fallback value for when the value is not known, do not use this value when making requests """

    def __str__(self) -> str:
        return str(self.value)

    @classmethod
    def _missing_(cls, number):
        return cls(cls.UNKNOWN)
