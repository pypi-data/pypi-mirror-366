# py_logger

A simple colored logger for Python.

## Installation

```bash
pip install .
```

## Usage

```python
from py_logger import get_logger

logger = get_logger(__name__)

logger.debug("This is a debug message.")
logger.info("This is an info message.")
logger.warning("This is a warning message.")
logger.error("This is an error message.")
logger.critical("This is a critical message.")
```

```python
from py_logger import get_logger

logger = get_logger(__name__, log_file=True) # logs to file

logger = get_logger(__name__, log_prints=True) # redirects prints to INFO


```
