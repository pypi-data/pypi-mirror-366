from typing import NamedTuple


class JobMetadata(NamedTuple):
    job_id: str | None
    job_queue: str
    compute_environment: str


class EnvironmentMetadata(NamedTuple):
    environment: str
    version: str
