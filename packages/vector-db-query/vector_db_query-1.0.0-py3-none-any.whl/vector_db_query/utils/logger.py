"""Logging configuration for Vector DB Query System."""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

from pythonjsonlogger import jsonlogger

from vector_db_query.utils.config import get_config


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output."""
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        # Get base format
        log_fmt = self._style._fmt
        
        # Add color if supported
        if sys.stdout.isatty() and record.levelname in self.COLORS:
            levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.RESET}"
            record.levelname = levelname
            
        # Format the record
        result = super().format(record)
        
        return result


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    json_logs: bool = False
) -> None:
    """Set up logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file. If None, uses config default
        json_logs: Whether to use JSON format for logs
    """
    config = get_config()
    
    # Determine log level
    if log_level is None:
        log_level = config.get("app.log_level", "INFO")
    log_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create logger
    logger = logging.getLogger("vector_db_query")
    logger.setLevel(log_level)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    if json_logs:
        # JSON formatter for console
        json_formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(name)s %(levelname)s %(message)s",
            datefmt=config.get("logging.date_format")
        )
        console_handler.setFormatter(json_formatter)
    else:
        # Colored formatter for console
        console_formatter = ColoredFormatter(
            config.get("logging.format"),
            datefmt=config.get("logging.date_format")
        )
        console_handler.setFormatter(console_formatter)
        
    logger.addHandler(console_handler)
    
    # File handler
    if log_file is None:
        log_dir = Path(config.get("paths.log_dir", "./logs"))
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "vector-db-query.log"
    else:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=config.get("logging.file_max_bytes", 10485760),
        backupCount=config.get("logging.file_backup_count", 5)
    )
    file_handler.setLevel(log_level)
    
    # Always use plain formatter for file logs
    file_formatter = logging.Formatter(
        config.get("logging.format"),
        datefmt=config.get("logging.date_format")
    )
    file_handler.setFormatter(file_formatter)
    
    logger.addHandler(file_handler)
    
    # Set up root logger to capture third-party logs
    logging.root.setLevel(logging.WARNING)
    logging.root.handlers = [console_handler, file_handler]
    
    # Log startup message
    logger.info(f"Logging initialized - Level: {logging.getLevelName(log_level)}")
    logger.info(f"Log file: {log_file}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f"vector_db_query.{name}")


# Convenience function for module-level logging
def log_debug(message: str, **kwargs) -> None:
    """Log debug message."""
    logger = get_logger("main")
    logger.debug(message, **kwargs)


def log_info(message: str, **kwargs) -> None:
    """Log info message."""
    logger = get_logger("main")
    logger.info(message, **kwargs)


def log_warning(message: str, **kwargs) -> None:
    """Log warning message."""
    logger = get_logger("main")
    logger.warning(message, **kwargs)


def log_error(message: str, **kwargs) -> None:
    """Log error message."""
    logger = get_logger("main")
    logger.error(message, **kwargs)


def log_critical(message: str, **kwargs) -> None:
    """Log critical message."""
    logger = get_logger("main")
    logger.critical(message, **kwargs)


# Initialize logging on import
setup_logging()