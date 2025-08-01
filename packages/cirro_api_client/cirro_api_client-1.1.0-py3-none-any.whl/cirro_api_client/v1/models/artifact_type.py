from enum import Enum


class ArtifactType(str, Enum):
    FILES = "FILES"
    """ Files used in the workflow """
    INGEST_MANIFEST = "INGEST_MANIFEST"
    """ Files expected to upload """
    METADATA = "METADATA"
    """ Snapshot of metadata at the time of execution """
    SAMPLE_SHEET = "SAMPLE_SHEET"
    """ Samples used in the workflow """
    WORKFLOW_COMPUTE_CONFIG = "WORKFLOW_COMPUTE_CONFIG"
    """ Compute overrides used in the workflow """
    WORKFLOW_DAG = "WORKFLOW_DAG"
    """ Direct acyclic graph of workflow execution """
    WORKFLOW_DEBUG_LOGS = "WORKFLOW_DEBUG_LOGS"
    """ Debug logs from workflow engine """
    WORKFLOW_LOGS = "WORKFLOW_LOGS"
    """ Logs from workflow engine """
    WORKFLOW_OPTIONS = "WORKFLOW_OPTIONS"
    """ Options used in the workflow """
    WORKFLOW_PARAMETERS = "WORKFLOW_PARAMETERS"
    """ Parameters used in the workflow """
    WORKFLOW_REPORT = "WORKFLOW_REPORT"
    """ Execution report from workflow engine """
    WORKFLOW_TIMELINE = "WORKFLOW_TIMELINE"
    """ Timeline of workflow execution """
    WORKFLOW_TRACE = "WORKFLOW_TRACE"
    """ Trace of workflow execution """
    UNKNOWN = "UNKNOWN"
    """ This is a fallback value for when the value is not known, do not use this value when making requests """

    def __str__(self) -> str:
        return str(self.value)

    @classmethod
    def _missing_(cls, number):
        return cls(cls.UNKNOWN)
