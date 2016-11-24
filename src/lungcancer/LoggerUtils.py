import logging
import os
from logging.handlers import RotatingFileHandler


class LoggerUtils:
    @staticmethod
    def get_logger(log_name):
        os.makedirs('logs', exist_ok=True)
        logger = logging.getLogger(log_name)
        logger.setLevel(logging.DEBUG)
        fh = RotatingFileHandler(os.path.join('logs', log_name + '.log'), mode='a', maxBytes=2 * 1024 * 1024,
                                 backupCount=4, encoding=None, delay=0)
        fh.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        logger.addHandler(fh)
        logger.addHandler(ch)
        return logger
