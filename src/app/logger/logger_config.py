# _*_ coding: utf-8 _*_
"""
Production-grade logging configuration module.

Features:
    - Daily rotating log files with date-stamped filenames
    - Unified console + file output
    - Uvicorn / FastAPI log compatibility
    - Automatic old-log cleanup (default 30 days)
    - Optional JSON format for log aggregation systems

Backwards compatibility:
    - ``setup_logger(name, level)`` and ``default_logger`` are still exported.
"""

import logging
import logging.handlers
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class DailyRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    """
    Daily-rotating file handler that produces filenames like ``app_2024-06-17.log``.
    """

    def __init__(
        self,
        log_dir: str | Path,
        filename_prefix: str = "app",
        backup_count: int = 30,
    ) -> None:
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.filename_prefix = filename_prefix
        self.log_file = self.log_dir / f"{filename_prefix}_{datetime.now().strftime('%Y-%m-%d')}.log"

        super().__init__(
            filename=str(self.log_file),
            when="midnight",
            interval=1,
            backupCount=backup_count,
            encoding="utf-8",
            delay=False,
        )

        self.suffix = "%Y-%m-%d"
        self.extMatch = r"^\d{4}-\d{2}-\d{2}$"  # noqa: W605

    def doRollover(self) -> None:
        """Override rollover logic to keep the date-stamped filename pattern."""
        if self.stream:
            self.stream.close()
            self.stream = None

        self.baseFilename = str(
            self.log_dir / f"{self.filename_prefix}_{datetime.now().strftime('%Y-%m-%d')}.log"
        )

        if not self.delay:
            self.stream = self._open()


# ---------------------------------------------------------------------------
# New-style API (inspired by reference log_config.py)
# ---------------------------------------------------------------------------

def setup_logging(
    log_dir: Optional[str | Path] = None,
    log_level: str = "INFO",
    filename_prefix: str = "app",
    backup_count: int = 30,
    console_output: bool = True,
    json_format: bool = False,
) -> logging.Logger:
    """
    Configure the root logger with daily rotation and optional console output.

    Args:
        log_dir: Directory for log files. Defaults to ``<this_file>/logs``.
        log_level: One of ``DEBUG``, ``INFO``, ``WARNING``, ``ERROR``.
        filename_prefix: Prefix for log file names.
        backup_count: Number of rotated log files to retain.
        console_output: Whether to also emit logs to stdout.
        json_format: Whether to use a flat format suitable for log shippers.

    Returns:
        The configured root logger.
    """
    if log_dir is None:
        log_dir = Path(__file__).parent / "logs"
    else:
        log_dir = Path(log_dir)

    log_dir.mkdir(parents=True, exist_ok=True)

    if json_format:
        log_format = "%(asctime)s %(name)s %(levelname)s %(message)s"
    else:
        log_format = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"

    formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers to avoid duplicates on re-import
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 1. Daily rotating file handler (all levels)
    file_handler = DailyRotatingFileHandler(
        log_dir=str(log_dir),
        filename_prefix=filename_prefix,
        backup_count=backup_count,
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)

    # 2. Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        root_logger.addHandler(console_handler)

    # 3. Uvicorn access log (separate file)
    access_log_file = log_dir / f"access_{datetime.now().strftime('%Y-%m-%d')}.log"
    access_handler = logging.handlers.TimedRotatingFileHandler(
        filename=str(access_log_file),
        when="midnight",
        interval=1,
        backupCount=backup_count,
        encoding="utf-8",
    )
    access_handler.setFormatter(formatter)
    access_handler.setLevel(logging.INFO)

    access_logger = logging.getLogger("uvicorn.access")
    access_logger.handlers = []
    access_logger.addHandler(access_handler)
    access_logger.propagate = False

    # 4. Uvicorn error log (separate file + console)
    error_log_file = log_dir / f"error_{datetime.now().strftime('%Y-%m-%d')}.log"
    error_handler = logging.handlers.TimedRotatingFileHandler(
        filename=str(error_log_file),
        when="midnight",
        interval=1,
        backupCount=backup_count,
        encoding="utf-8",
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)

    uvicorn_logger = logging.getLogger("uvicorn.error")
    uvicorn_logger.handlers = []
    uvicorn_logger.addHandler(error_handler)
    if console_output:
        uvicorn_logger.addHandler(console_handler)
    uvicorn_logger.propagate = False

    return root_logger


def get_uvicorn_log_config(
    log_dir: Optional[str | Path] = None,
    filename_prefix: str = "app",
    backup_count: int = 30,
) -> dict:
    """
    Generate a Uvicorn-compatible ``log_config`` dictionary.

    Can be passed directly to ``uvicorn.run(..., log_config=...)``.
    """
    if log_dir is None:
        log_dir = Path(__file__).parent / "logs"
    else:
        log_dir = Path(log_dir)

    log_dir.mkdir(parents=True, exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "access": {
                "format": "%(asctime)s | %(levelname)-8s | %(client_addr)s | %(request_line)s | %(status_code)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "default": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "formatter": "default",
                "filename": str(log_dir / f"{filename_prefix}_{today}.log"),
                "when": "midnight",
                "interval": 1,
                "backupCount": backup_count,
                "encoding": "utf-8",
            },
            "access": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "formatter": "access",
                "filename": str(log_dir / f"access_{today}.log"),
                "when": "midnight",
                "interval": 1,
                "backupCount": backup_count,
                "encoding": "utf-8",
            },
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "uvicorn": {
                "handlers": ["default", "console"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["access", "console"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.error": {
                "handlers": ["default", "console"],
                "level": "INFO",
                "propagate": False,
            },
            "app": {
                "handlers": ["default", "console"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }


# ---------------------------------------------------------------------------
# Legacy API (retained for backwards compatibility)
# ---------------------------------------------------------------------------

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def setup_logger(name: Optional[str] = None, level: int = logging.INFO) -> logging.Logger:
    """
    Set up and return a logger with console + daily-rotating file output.

    Args:
        name: Logger name (usually ``__name__``). Defaults to ``"app"``.
        level: Logging level. Defaults to ``logging.INFO``.

    Returns:
        A configured logger instance.
    """
    logger_name = name or "app"
    logger = logging.getLogger(logger_name)

    # If handlers already exist, assume the logger has been configured
    if logger.handlers:
        return logger

    logger.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    # Daily rotating file handler (per-logger file)
    file_handler = DailyRotatingFileHandler(
        log_dir=LOG_DIR,
        filename_prefix=logger_name,
        backup_count=30,
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# Default module-level logger (legacy)
default_logger = setup_logger("app")
