from datetime import datetime
from google.auth.exceptions import DefaultCredentialsError
from google.cloud import error_reporting, logging
import logging as stdlib_logging
from pydantic import BaseModel, Field
import pytz
import sys
from typing import Literal, Tuple

LOG_LEVEL = Literal["CRITICAL", "DEBUG", "ERROR", "FATAL", "INFO", "TRACE", "WARNING"]


class LogMessage(BaseModel):
    context: str = Field(description="The context of the log message")
    message: str = Field(description="The message of the log message")
    serialized_data: str = Field(description="The serialized data of the log message")
    severity: LOG_LEVEL = Field(description="The severity of the log message")
    time: str = Field(
        default_factory=lambda: datetime.now(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S"),
        description="The time of the log message",
    )


class ErrorLogMessage(LogMessage):
    # allow arbitrary types like Exception to be used in Pydantic models
    model_config = {"arbitrary_types_allowed": True}
    
    error: Exception = Field(description="The error of the log message")
    severity: Literal["ERROR"] = "ERROR"


def get_loggers(
    service_name: str,
) -> Tuple[error_reporting.Client | None, logging.Logger | None, stdlib_logging.Logger]:
    try:
        gcp_error_reporting_client = error_reporting.Client()
        log_name = service_name
        logging_client = logging.Client()
        gcp_logger = logging_client.logger(log_name)
    except DefaultCredentialsError:
        # this means we're not running in GCP, so we don't need to use GCP loggers
        gcp_error_reporting_client = None
        gcp_logger = None

    stdlib_logger = stdlib_logging.getLogger(service_name)
    # setting the minimum level to DEBUG to capture all messages
    stdlib_logger.setLevel(stdlib_logging.DEBUG)
    # clear any existing handlers
    stdlib_logger.handlers.clear()

    # create `stdlib_logging` formatter
    formatter = stdlib_logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # create stdout handler for non-error messages (DEBUG, INFO, WARNING)
    stdout_handler = stdlib_logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(stdlib_logging.DEBUG)
    stdout_handler.setFormatter(formatter)
    stdout_handler.addFilter(lambda record: record.levelno < stdlib_logging.ERROR)

    # create stderr handler for error messages (ERROR, CRITICAL)
    stderr_handler = stdlib_logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(stdlib_logging.ERROR)
    stderr_handler.setFormatter(formatter)

    # add handlers to logger
    stdlib_logger.addHandler(stdout_handler)
    stdlib_logger.addHandler(stderr_handler)

    return gcp_error_reporting_client, gcp_logger, stdlib_logger


def log_err(
    error: ErrorLogMessage,
    stdlib_logger: stdlib_logging.Logger,
    gcp_error_reporting_client: error_reporting.Client | None,
):
    stdlib_logger.error(error.message, exc_info=error.error)
    if gcp_error_reporting_client:
        gcp_error_reporting_client.report_exception(error.model_dump(mode="json"))
    else:
        stdlib_logger.log(
            severity_to_int_level("WARNING"), "could not report error to GCP"
        )


def log_out(
    log_msg: LogMessage,
    stdlib_logger: stdlib_logging.Logger,
    gcp_logger: logging.Logger | None,
):
    stdlib_logger.log(severity_to_int_level(log_msg.severity), log_msg.message)
    if gcp_logger:
        gcp_logger.log_struct(log_msg.model_dump())
    else:
        stdlib_logger.log(
            severity_to_int_level("WARNING"),
            "could not log output to GCP",
        )


def severity_to_int_level(severity: LOG_LEVEL) -> int:
    return {
        "CRITICAL": stdlib_logging.CRITICAL,
        "DEBUG": stdlib_logging.DEBUG,
        "ERROR": stdlib_logging.ERROR,
        "FATAL": stdlib_logging.FATAL,
        "INFO": stdlib_logging.INFO,
        "TRACE": stdlib_logging.DEBUG,
        "WARNING": stdlib_logging.WARNING,
    }[severity]
