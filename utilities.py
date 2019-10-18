import os
import logging


class Logger(object):
    def __init__(self, name=__name__, log_path='tmp', log_file='out.log',
                 logger_level=logging.DEBUG, file_level=logging.DEBUG,
                 stream_level=logging.ERROR, date_format='%Y-%m-%d %H:%M:%S',
                 log_format='%(asctime)s - %(name)s - ' +
                            '%(levelname)s - %(message)s'):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logger_level)
        fh = logging.FileHandler(os.path.join(log_path, name + '-' + log_file))
        fh.setLevel(file_level)
        ch = logging.StreamHandler()
        ch.setLevel(stream_level)
        formatter = logging.Formatter(log_format, datefmt=date_format)
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)
        if not self.logger.handlers:
            self.logger.addHandler(ch)
            self.logger.addHandler(fh)

    def critical(self, message):
        return self.logger.critical(message)

    def debug(self, message):
        return self.logger.debug(message)

    def error(self, message):
        return self.logger.error(message)

    def exception(self, message):
        return self.logger.exception(message)

    def info(self, message):
        return self.logger.info(message)

    def warning(self, message):
        return self.logger.warning(message)