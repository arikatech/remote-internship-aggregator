import logging
import sys
from pythonjsonlogger import jsonlogger


def setup_logging(log_level: str) -> None:
    root = logging.getLogger()
    root.setLevel(log_level.upper())

    handler = logging.StreamHandler(sys.stdout)

    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s"
    )

    handler.setFormatter(formatter)
    root.handlers = [handler]
