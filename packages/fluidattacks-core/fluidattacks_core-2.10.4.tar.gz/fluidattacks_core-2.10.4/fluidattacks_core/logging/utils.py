import logging
import os

from fluidattacks_core.logging.types import EnvironmentMetadata, JobMetadata


class BatchOnlyFilter(logging.Filter):
    def filter(self, _record: logging.LogRecord) -> bool:
        return os.environ.get("AWS_BATCH_JOB_ID") is not None


class NoBatchFilter(logging.Filter):
    def filter(self, _record: logging.LogRecord) -> bool:
        return os.environ.get("AWS_BATCH_JOB_ID") is None


class ColorfulFormatter(logging.Formatter):
    grey: str = "\x1b[38;1m"
    yellow: str = "\x1b[33;1m"
    red: str = "\x1b[31;1m"
    reset: str = "\x1b[0m"
    msg_format: str = "{asctime} [{levelname}] [{name}] {message}"

    FORMATS = {  # noqa: RUF012
        logging.DEBUG: grey + msg_format + reset,
        logging.INFO: msg_format,
        logging.WARNING: yellow + msg_format + reset,
        logging.ERROR: red + msg_format + reset,
        logging.CRITICAL: red + msg_format + reset,
    }

    def format(self, record: logging.LogRecord) -> str:
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(
            log_fmt,
            datefmt=self.datefmt,
            style="{",
        )
        return formatter.format(record)


def get_job_metadata() -> JobMetadata:
    """Get the job metadata for applications running in batch environments."""
    return JobMetadata(
        job_id=os.environ.get("AWS_BATCH_JOB_ID"),
        job_queue=os.environ.get("AWS_BATCH_JQ_NAME", "default"),
        compute_environment=os.environ.get("AWS_BATCH_CE_NAME", "default"),
    )


def get_environment_metadata() -> EnvironmentMetadata:
    """Get the environment metadata for applications running in batch environments."""
    environment = (
        "production" if os.environ.get("CI_COMMIT_REF_NAME", "trunk") == "trunk" else "development"
    )
    commit_sha = os.environ.get("CI_COMMIT_SHA", "00000000")
    commit_short_sha = commit_sha[:8]

    return EnvironmentMetadata(
        environment=environment,
        version=commit_short_sha,
    )


def debug_logs() -> None:
    """Test all the log levels in the root logger and a custom logger."""
    root_logger = logging.getLogger()

    root_logger.debug("This is a debug log")
    root_logger.info("This is an info log")
    root_logger.warning("This is a warning log")
    root_logger.error("This is an error log")
    root_logger.critical("This is a critical log")

    logger = logging.getLogger("test-logger")
    logger.debug("This is a debug log")
    logger.info("This is an info log")
    logger.warning("This is a warning log")
    logger.error("This is an error log")
    logger.critical("This is a critical log")

    try:
        raise KeyError("missing_key")  # noqa: TRY301
    except KeyError as e:
        root_logger.exception(e)
        logger.exception(e)
