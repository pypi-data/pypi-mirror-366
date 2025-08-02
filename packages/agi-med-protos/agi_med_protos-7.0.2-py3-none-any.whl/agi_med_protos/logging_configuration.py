import sys
from enum import StrEnum, auto

from loguru import logger


class LogLevelEnum(StrEnum):
    @staticmethod
    def _generate_next_value_(name: str, start: int, count: int, last_values: list[str]) -> str:
        return name.upper()

    TRACE = auto()
    DEBUG = auto()
    INFO = auto()
    SUCCESS = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()


def init_logger(log_level: LogLevelEnum):
    logger.remove()
    extra = {"request_id": "SYSTEM_LOG"}
    format_ = "{time:DD-MM-YYYY HH:mm:ss} | <level>{level: <8}</level> | {extra[request_id]}"
    format_ = f"{format_} | <level>{{message}}</level>"
    logger.add(sys.stdout, colorize=True, format=format_, level=log_level)
    logger.configure(extra=extra)
