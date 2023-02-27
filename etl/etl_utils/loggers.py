import logging
from pathlib import Path
from typing import Optional, Union


def setup_logger(
    name: str, log_file: Optional[Union[str, Path]] = None, level: int = logging.INFO
) -> logging.Logger:
    """Creates a logger.

    Args:
        name (str):
            logger name.
        log_file (Optional[Union[str, Path]], optional):
            path to log file. Defaults to None. Logs are written to stdout.
        level (int, optional): logging level. Defaults to logging.INFO.

    Returns:
        logging.Logger: _description_
    """

    logger = logging.getLogger(name)

    if log_file:
        handler: logging.Handler = logging.FileHandler(log_file)
    else:
        handler = logging.StreamHandler()

    formatter = logging.Formatter(
        '%(asctime)s [%(name)-12s] %(levelname)-8s %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.setLevel(level)
    return logger
