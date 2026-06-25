import logging
import os
from pathlib import Path


class GameLogger:
    """Simple logging utility for the RPG Game."""

    _logger = None
    _initialized = False

    @classmethod
    def get_logger(cls, name="RPGGame"):
        """Get or create logger instance."""
        if cls._logger is not None:
            return cls._logger

        cls._logger = logging.getLogger(name)
        cls._logger.setLevel(logging.DEBUG)

        # Create logs directory if it doesn't exist
        log_dir = Path(__file__).resolve().parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)

        log_file = log_dir / "game.log"

        # File handler
        file_handler = logging.FileHandler(
            log_file,
            encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        cls._logger.addHandler(file_handler)
        cls._logger.addHandler(console_handler)

        cls._initialized = True
        cls._logger.info("Game logger initialized")

        return cls._logger

    @classmethod
    def info(cls, message):
        """Log info message."""
        logger = cls.get_logger()
        logger.info(message)

    @classmethod
    def debug(cls, message):
        """Log debug message."""
        logger = cls.get_logger()
        logger.debug(message)

    @classmethod
    def warning(cls, message):
        """Log warning message."""
        logger = cls.get_logger()
        logger.warning(message)

    @classmethod
    def error(cls, message):
        """Log error message."""
        logger = cls.get_logger()
        logger.error(message)

    @classmethod
    def critical(cls, message):
        """Log critical message."""
        logger = cls.get_logger()
        logger.critical(message)
