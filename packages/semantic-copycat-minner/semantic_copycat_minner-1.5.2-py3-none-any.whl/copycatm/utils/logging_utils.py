"""
Logging utilities for CopycatM.
"""

import logging
import sys
from typing import Optional


def setup_logging(level: str = "INFO", 
                  format_string: Optional[str] = None,
                  log_file: Optional[str] = None) -> None:
    """Setup logging configuration for CopycatM."""
    
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Add file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(format_string))
        logging.getLogger().addHandler(file_handler)
    
    # Set specific logger levels
    logging.getLogger("copycatm").setLevel(logging.DEBUG)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""
    return logging.getLogger(f"copycatm.{name}")


def log_analysis_start(file_path: str, logger: Optional[logging.Logger] = None) -> None:
    """Log the start of file analysis."""
    if logger is None:
        logger = get_logger("analyzer")
    logger.info(f"Starting analysis of {file_path}")


def log_analysis_complete(file_path: str, duration: float, 
                         algorithms_found: int, logger: Optional[logging.Logger] = None) -> None:
    """Log the completion of file analysis."""
    if logger is None:
        logger = get_logger("analyzer")
    logger.info(f"Completed analysis of {file_path} in {duration:.2f}s - found {algorithms_found} algorithms")


def log_error(error: Exception, file_path: Optional[str] = None, 
              logger: Optional[logging.Logger] = None) -> None:
    """Log an error with context."""
    if logger is None:
        logger = get_logger("error")
    
    context = f" in {file_path}" if file_path else ""
    logger.error(f"Error{context}: {str(error)}", exc_info=True)


def log_warning(message: str, file_path: Optional[str] = None,
                logger: Optional[logging.Logger] = None) -> None:
    """Log a warning with context."""
    if logger is None:
        logger = get_logger("warning")
    
    context = f" in {file_path}" if file_path else ""
    logger.warning(f"Warning{context}: {message}")


def log_debug(message: str, logger: Optional[logging.Logger] = None) -> None:
    """Log a debug message."""
    if logger is None:
        logger = get_logger("debug")
    logger.debug(message) 