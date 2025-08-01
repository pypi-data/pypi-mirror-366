from __future__ import annotations

import logging
import sys
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any

try:
    from loguru import logger
except ImportError:
    raise ImportError(
        "The `loguru` extra must be installed to use the `compose.logging` module. "
        "Install `compose` with `loguru` extra (`compose[loguru]`)"
    )

if TYPE_CHECKING:
    from loguru import Logger


class InterceptHandler(logging.Handler):
    """https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging"""  # noqa: E501

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

    def filter(self, record: logging.LogRecord) -> bool:
        return "/health-check" not in record.getMessage()


def intercept_logging(intercept_handler: InterceptHandler, log_level: int) -> None:
    """Python 내장 logging 모듈을 loguru로 대체합니다. (해당 함수를 호출하려면 `loguru`를 설치해야 합니다.)"""
    logging.basicConfig(handlers=[intercept_handler], level=log_level, force=True)


def intercept(
    intercept_handler: InterceptHandler,
    log_names: Iterable[str] = (
        "gunicorn.error",
        "gunicorn.access",
        "uvicorn.error",
        "uvicorn.access",
    ),
) -> None:
    intercept_logging(intercept_handler=intercept_handler, log_level=logging.INFO)
    for name in log_names:
        logging.getLogger(name).handlers = [intercept_handler]


def get_default_logging_config(serialize_log: bool) -> dict[str, Any]:
    non_serialized_format = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | <level>{level: <8}</level> | <level>{message}</level>"
    )
    return {
        "sink": sys.stdout,
        "diagnose": False,
        "format": "{message}" if serialize_log else non_serialized_format,
        "serialize": serialize_log,
    }


def get_default_logger(
    log_level: int,
    serialize_log: bool,
    **config: Any,
) -> Logger:
    intercept_handler = InterceptHandler()
    logging.basicConfig(handlers=[intercept_handler], level=log_level, force=True)
    intercept(intercept_handler=intercept_handler)
    logger.configure(
        handlers=[
            {
                **get_default_logging_config(serialize_log),
                **config,
            }
        ]
    )
    return logger
