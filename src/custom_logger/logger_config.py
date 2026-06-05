import logging
import os
from datetime import datetime
from pathlib import Path
import sys

LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
LOG_DIR_PATH = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR_PATH.mkdir(parents=True, exist_ok=True) 

LOG_FILE_PATH = LOG_DIR_PATH / LOG_FILE 

#Clean any existing handlers to ensure our configuration takes precedence
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)  

if root_logger.hasHandlers():
    root_logger.handlers.clear()

#Define a unified format string
log_formatter = logging.Formatter(
    fmt="[ %(asctime)s ] %(lineno)d %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
    )

#File handler for writing logs to a file
file_handler = logging.FileHandler(LOG_FILE_PATH, encoding='utf-8')
file_handler.setFormatter(log_formatter)
root_logger.addHandler(file_handler)

#Console handler for outputting logs to the terminal
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_formatter)
root_logger.addHandler(console_handler)

logging.info(f"Logging initialized. Logs are being written to: {LOG_FILE_PATH}")

# Global Scope: Because you attached the handlers to the root_logger (using logging.getLogger()) in your config file, every other file that calls logging.getLogger(__name__) will automatically send its data to those same handlers. This means that any log message generated in your tools.py or any other module will be captured by the file and console handlers you set up in logger_config.py, ensuring a consistent logging experience across your entire application.
# Older approach had a problem where if any third-party library (like langchain) initialized logging before your config file runs, it would set up its own handlers and configurations, causing your basicConfig call to be ignored. By explicitly clearing existing handlers and setting up your own, you ensure that all logs, including those from third-party libraries, are captured in your log files and console output as intended.