import logging

import sys


def initialize_logging():
    handlers = []

    stream_handler = logging.StreamHandler(sys.stdout)
    handlers.append(stream_handler)

    # noinspection PyArgumentList
    logging.basicConfig(level="DEBUG", handlers=handlers)
