from typing import override
import logging

class TruncateFilenameFormatter(logging.Formatter):
    @override
    def format(self, record: logging.LogRecord):
        record.short_filename = record.filename[:10]
        return super().format(record)


def setup_log(
    name: str = "app",
    level: int = logging.INFO,
) -> logging.Logger:

    log = logging.getLogger(name)
    log.setLevel(level)

    # Avoid adding duplicate handlers
    if log.handlers:
        return log

    formatter = TruncateFilenameFormatter(
        fmt="%(asctime)s | %(levelname)-5s | %(short_filename)-10s:%(lineno)-4d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    log.addHandler(console_handler)
    log.propagate = False

    return log

# Singleton root log
log = setup_log()