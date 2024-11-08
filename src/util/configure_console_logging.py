import logging
import sys

import colorlog


console_formatter = colorlog.ColoredFormatter(
    "{log_color}{levelname}{reset}:{blue}{name}{reset}:{message}",
    style="{",
)

def stdout_filter(record: logging.LogRecord) -> bool:
    return record.levelno <= logging.INFO
console_message_handler = logging.StreamHandler(sys.stdout)
console_message_handler.setLevel(logging.DEBUG)
console_message_handler.addFilter(stdout_filter)
console_message_handler.setFormatter(console_formatter)

console_error_handler = colorlog.StreamHandler(sys.stderr)
console_error_handler.setLevel(logging.WARN)
console_error_handler.setFormatter(console_formatter)


def configure_console_logging(logger: logging.Logger) -> None:
    logger.addHandler(console_message_handler)
    logger.addHandler(console_error_handler)


__all__ = ("configure_console_logging",)
