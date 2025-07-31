__version__ = '1.14.0'

import logging
from logging.handlers import RotatingFileHandler


def set_file_logger(
        file_name, name='ks3', level=logging.INFO,
        format_string=None, max_bytes=1024 * 1024 * 500, backup_count=5
):
    if not format_string:
        format_string = '%(asctime)s %(name)s:%(lineno)s [%(levelname)s] %(thread)d - %(funcName)s: %(message)s'
    logger = logging.getLogger(name)
    logger.setLevel(level)
    fh = RotatingFileHandler(filename=file_name, maxBytes=max_bytes, backupCount=backup_count)
    fh.setLevel(level)
    formatter = logging.Formatter(format_string)
    fh.setFormatter(formatter)
    logger.addHandler(fh)


def set_stream_logger(name='ks3', level=logging.INFO, format_string=None):
    if not format_string:
        format_string = '%(asctime)s %(name)s:%(lineno)s [%(levelname)s] %(thread)d - %(funcName)s: %(message)s'
    logger = logging.getLogger(name)
    logger.setLevel(level)
    sh = logging.StreamHandler()
    sh.setLevel(level)
    formatter = logging.Formatter(format_string)
    sh.setFormatter(formatter)
    logger.addHandler(sh)
