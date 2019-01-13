import logging


class PrintHandler(logging.Handler):
    def emit(self, record):
        msg = self.format(record)
        print(msg)


def setup_logging():
    logger = logging.getLogger()
    logger.addHandler(PrintHandler())
    return logger