import logging
import logging.config

from snakestack.config import settings
from snakestack.logging.formatters import FORMATTERS
from snakestack.logging.handlers import HANDLERS

DEFAULT_LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": FORMATTERS,
    "handlers": HANDLERS,
    "root": {
        "level": settings.snakestack_log_level,
        "handlers": ["console"]
    }
}


def setup_logging() -> None:
    logging.config.dictConfig(DEFAULT_LOGGING_CONFIG)
