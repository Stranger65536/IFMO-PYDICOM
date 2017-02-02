# coding=utf-8
from logging import DEBUG
from logging import Formatter
from logging import INFO
from logging import StreamHandler
from logging import getLogger
from logging.handlers import RotatingFileHandler
from os import makedirs
from os.path import join


class LoggerUtils:
    @staticmethod
    def get_logger(log_name):
        makedirs('logs', exist_ok=True)
        logger = getLogger(log_name)
        logger.setLevel(DEBUG)
        name = join('logs', log_name + '.log')
        fh = RotatingFileHandler(filename=name,
                                 maxBytes=8 * 1024 * 1024,
                                 backupCount=4, encoding='utf-8',
                                 delay=0)
        fh.setLevel(DEBUG)
        ch = StreamHandler()
        ch.setLevel(INFO)
        formatter = Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        logger.addHandler(fh)
        logger.addHandler(ch)
        return logger
