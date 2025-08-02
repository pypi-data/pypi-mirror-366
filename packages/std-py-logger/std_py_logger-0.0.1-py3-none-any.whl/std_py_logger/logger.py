import logging
import sys
from datetime import datetime

class ColoredFormatter(logging.Formatter):
    """
    A custom formatter to add colors to log messages.
    """
    COLORS = {
        'DEBUG': '\033[94m',    # Blue
        'INFO': '\033[92m',     # Green
        'WARNING': '\033[93m',  # Yellow
        'CRITICAL': '\033[95m', # Magenta 
        'ERROR': '\033[91m',    # Red
        'ENDC': '\033[0m',
    }

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.COLORS['ENDC'])
        message = super().format(record)
        return f"{color}{message}{self.COLORS['ENDC']}"

def get_logger(name:str, log_file=False, log_prints=False, capture_warnings=False):
    """creates a logger

    Args:
        name (str): name of the logger
        log_file (bool, optional): If True it will log to file
        log_prints (bool, optional): Redirects print statements to log INFO
        capture_warnings (bool, optional): If True it will capture warnings

    Returns:
        _type_: _description_
    """
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        return logger
        
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(ColoredFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(ch)

    if log_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        fh = logging.FileHandler(f'py_logger_{timestamp}.log')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(ColoredFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(fh)

    if log_prints:
        sys.stdout = PrintLogger(logger)

    if capture_warnings:
        logging.captureWarnings(True)
        warnings_logger = logging.getLogger('py.warnings')
        warnings_logger.addHandler(ch)

    return logger

class PrintLogger:
    """
    A class to redirect print statements to a logger.
    """
    def __init__(self, logger):
        self.logger = logger

    def write(self, message):
        if message.strip():
            self.logger.info(message.strip())

    def flush(self):
        pass
