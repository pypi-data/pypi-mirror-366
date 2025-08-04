import logging
import sys
from typing import Callable
from .not_chalk import NotChalk

try:
    from simple_chalk import chalk  # type: ignore
except Exception:
    chalk = NotChalk()


class LevelFilter(logging.Filter):
    def __init__(self, level):
        self.level = level

    def filter(self, record):
        return record.levelno == self.level


def __handler(
    level: int,
    format: str,
    stream=sys.stdout,
    color: Callable = chalk.white,
    message_color: Callable = lambda v: v,
):
    handler = logging.StreamHandler(stream)
    handler.setLevel(level)

    a = chalk.whiteBright.bold("%(name)s")
    b = chalk.gray.dim(".")
    c = color("%(levelname)s")
    d = chalk.gray.dim("%(asctime)s.%(msecs)03d")
    e = message_color("%(message)s")
    formatter = logging.Formatter(
        format.format(a, b, c, d, e),
        datefmt="%H:%M:%S",
    )

    handler.addFilter(LevelFilter(level))
    handler.setFormatter(formatter)

    return handler


def new(name: str):
    logger = logging.Logger(name, logging.DEBUG)
    format = "[{0}{1}{2}] {3} {4}"

    if not name.strip():
        format = "[{2}] {3} {4}"

    logger.addHandler(
        __handler(
            logging.DEBUG,
            format,
            color=chalk.gray.dim,
            message_color=chalk.gray.dim,
        )
    )

    logger.addHandler(
        __handler(
            logging.INFO,
            format,
            color=chalk.blue,
        )
    )

    logger.addHandler(
        __handler(
            logging.WARNING,
            format,
            color=chalk.yellow,
            message_color=chalk.yellow,
        )
    )

    logger.addHandler(
        __handler(
            logging.ERROR,
            format,
            color=chalk.red,
            message_color=chalk.red,
        )
    )

    logger.addHandler(
        __handler(
            logging.CRITICAL,
            format,
            color=chalk.red.bold,
            message_color=chalk.red.bold,
        )
    )

    return logger
