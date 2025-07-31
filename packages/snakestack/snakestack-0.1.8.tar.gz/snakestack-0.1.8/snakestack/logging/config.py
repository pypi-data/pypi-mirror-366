import logging.config
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from snakestack.config import settings


class LoggerSettings(BaseModel):
    version: int = 1
    disable_existing_loggers: bool = False
    formatters: Dict[str, Any] = Field(default_factory=lambda: {
        "default": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
        "with_request_id": {
            "format": (
                "%(asctime)s [%(levelname)s] [req_id=%(request_id)s] "
                "%(name)s: %(message)s"
            )
        }
    })
    handlers: Dict[str, Any] = Field(default_factory=lambda: {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        }
    })
    filters: Dict[str, Any] = Field(default_factory=dict)
    root: Dict[str, Any] = Field(default_factory=lambda: {
        "level": settings.snakestack_log_level,
        "handlers": ["console"]
    })


class LoggerConfigurator:
    def __init__(self: "LoggerConfigurator", base: Optional[LoggerSettings] = None) -> None:
        self.config = base or LoggerSettings()

    def add_formatter(self: "LoggerConfigurator", name: str, formatter: Dict[str, Any]) -> None:
        self.config.formatters[name] = formatter

    def add_handler(self: "LoggerConfigurator", name: str, handler: Dict[str, Any]) -> None:
        self.config.handlers[name] = handler

    def add_filter(self: "LoggerConfigurator", name: str, filter_config: Dict[str, Any]) -> None:
        self.config.filters[name] = filter_config

    def apply(self: "LoggerConfigurator") -> None:
        logging.config.dictConfig(self.config.model_dump())


def setup_logging() -> None:
    LoggerConfigurator().apply()
