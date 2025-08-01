import logging


class Formatter(logging.Formatter):  # pragma: no cover
    grey = "\x1b[38;20m"  # ] closing bracket for IDE
    yellow = "\x1b[33;20m"  # ] closing bracket for IDE
    red = "\x1b[31;20m"  # ] closing bracket for IDE
    blue = "\x1b[34;20m"  # ] closing bracket for IDE
    bold_red = "\x1b[31;1m"  # ] closing bracket for IDE
    reset = "\x1b[0m"  # ] closing bracket for IDE
    fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + fmt + reset,
        logging.INFO: blue + fmt + reset,
        logging.WARNING: yellow + fmt + reset,
        logging.ERROR: red + fmt + reset,
        logging.CRITICAL: bold_red + fmt + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

