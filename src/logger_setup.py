import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(log_file):
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,  # could be DEBUG, INFO, WARNING, ERROR, CRITICAL
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            RotatingFileHandler(log_file, maxBytes=5_000_000, backupCount=3),
            logging.StreamHandler()  # optional: also print to console
        ]
    )
