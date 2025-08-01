from enum import Enum


class ProjectAccessType(str, Enum):
    DATASET_UPLOAD = "DATASET_UPLOAD"
    PROJECT_DOWNLOAD = "PROJECT_DOWNLOAD"
    REFERENCE_UPLOAD = "REFERENCE_UPLOAD"
    SAMPLESHEET_UPLOAD = "SAMPLESHEET_UPLOAD"
    SHARED_DATASET_DOWNLOAD = "SHARED_DATASET_DOWNLOAD"
    UNKNOWN = "UNKNOWN"
    """ This is a fallback value for when the value is not known, do not use this value when making requests """

    def __str__(self) -> str:
        return str(self.value)

    @classmethod
    def _missing_(cls, number):
        return cls(cls.UNKNOWN)
