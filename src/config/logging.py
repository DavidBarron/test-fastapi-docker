import logging
import sys

from src.config import get_settings


def init_logging() -> None:
    settings = get_settings()

    logging.basicConfig(
        stream=sys.stdout,
        format="%(levelname)s:\t\t%(asctime)s\t\t%(name)s:\t%(message)s",  # noqa: E501
        level=settings.log_level,
    )
