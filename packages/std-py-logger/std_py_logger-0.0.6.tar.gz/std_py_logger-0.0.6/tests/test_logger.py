import unittest
import logging
from std_py_logger import get_logger
from unittest.mock import patch, mock_open

class TestLogger(unittest.TestCase):

    def test_get_logger(self):
        logger = get_logger('test_logger')
        self.assertIsInstance(logger, logging.Logger)

    def test_log_levels(self):
        with patch('sys.stdout') as mock_stdout:
            logger = get_logger('test_levels')
            logger.debug("debug message")
            logger.info("info message")
            logger.warning("warning message")
            logger.error("error message")
            logger.critical("critical message")
            self.assertEqual(mock_stdout.write.call_count, 5)

    def test_log_to_file(self):
        with patch('logging.FileHandler') as mock_file_handler:
            mock_file_handler.return_value.level = logging.DEBUG
            logger = get_logger('test_file_logger', log_file=True)
            logger.info("test file message")
            mock_file_handler.assert_called_once()

    def test_log_prints(self):
        logger = get_logger('test_print_logger', log_prints=True)
        with patch.object(logger, 'info') as mock_info:
            print("test print message")
            mock_info.assert_called_once_with("test print message")

if __name__ == '__main__':
    unittest.main()
