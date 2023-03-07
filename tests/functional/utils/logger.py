import logging

LOG_FORMAT = '%(asctime)s - %(levelname)s - %(funcName)s: %(lineno)d ' '- %(message)s'

logging.basicConfig(
    level=logging.INFO,
    encoding='utf-8',
    datefmt='%d.%m.%y %H:%M:%S',
    format=LOG_FORMAT,
)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    return logger
