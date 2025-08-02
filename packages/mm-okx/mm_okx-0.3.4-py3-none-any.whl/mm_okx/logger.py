import logging

from rich.logging import RichHandler


class ExtraFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        base = super().format(record)
        extras = {
            key: value
            for key, value in record.__dict__.items()
            if key not in logging.LogRecord.__dict__
            and key
            not in (
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "exc_info",
                "exc_text",
                "stack_info",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "message",
                "taskName",
                "asctime",
            )
        }
        if extras:
            extras_str = " | " + " ".join(f"{k}={v}" for k, v in extras.items())
            return base + extras_str
        return base


def configure_debug_logging() -> None:
    """
    Configure the root logger with a custom formatter that includes extra fields.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    console_handler = RichHandler(rich_tracebacks=True, show_time=True, show_level=True, show_path=False)
    console_handler.setFormatter(ExtraFormatter("{message}", style="{"))

    logger.addHandler(console_handler)
