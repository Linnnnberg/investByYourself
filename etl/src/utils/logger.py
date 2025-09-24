"""
Logging Utilities
InvestByYourself Financial Platform

Provides structured logging configuration for ETL operations.
"""

import logging
import logging.handlers
import os
from datetime import datetime
from typing import Optional


def setup_logging(name: str, log_level: str = "INFO") -> logging.Logger:
    """Set up structured logging for ETL operations."""

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))

    # Clear existing handlers
    logger.handlers.clear()

    # Create formatters
    detailed_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    json_formatter = logging.Formatter(
        '{"timestamp": "%(asctime)s", "logger": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}',
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(detailed_formatter)
    logger.addHandler(console_handler)

    # File handler (if log directory exists)
    log_file = os.getenv("ETL_LOG_FILE", "/app/logs/etl.log")
    log_dir = os.path.dirname(log_file)

    if os.path.exists(log_dir):
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5  # 10MB
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)

    return logger


class ETLFormatter(logging.Formatter):
    """Custom formatter for ETL operations."""

    def format(self, record):
        # Add ETL context to log record
        record.etl_timestamp = datetime.now().isoformat()
        record.etl_operation = getattr(record, "etl_operation", "unknown")

        return super().format(record)
