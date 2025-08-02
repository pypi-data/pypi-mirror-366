from std_py_logger import get_logger

logger = get_logger(__name__)

logger.debug("This is a debug message.")
logger.info("This is an info message.")
logger.warning("This is a warning message.")
logger.error("This is an error message.")
logger.critical("This is a critical message.")

file_logger = get_logger("file_logger", log_file=True)
file_logger.info("This message will be in the console and in a file.")

print_logger = get_logger("print_logger", log_prints=True)
print("This print statement will be logged as INFO.")

warnings_logger = get_logger("warnings_logger", capture_warnings=True)
import warnings
warnings.warn("This is a warning from the warnings module.")
