"""Logging configuration."""

import logging
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from loguru import Logger

from typeguard import typechecked


class LoggerProxy:
    """
    A proxy class for logging.Logger or loguru.Logger.

    This class allows for a unified interface to access either standard logging
    or Loguru logging. It supports lazy initialization and caching of the
    logger instance.
    """

    def __init__(self) -> None:
        self._logger: logging.Logger | Logger | None = None

    def is_initialized(self) -> bool:
        """
        Check if the logger has been initialized.

        Returns:
            bool: True if the logger is initialized, False otherwise.
        """
        return self._logger is not None

    @typechecked
    def setup_logger(
        self,
        package: str,
        log_file: str | Path,
        debug: bool = False,
        verbose: bool = False,
        use_loguru: bool = False,
        cache: bool = True,
    ) -> None:
        """
        Set up a configured logger instance using either `logging` or `loguru`.

        Args:
            package (str): The name of the package or project.
            log_file (str | Path): The path to the log file.
            debug (bool): Whether to enable debug-level logging.
            verbose (bool): Whether to enable verbose logging.
            use_loguru (bool): Whether to use `loguru` instead of the standard `logging` module.
            cache (bool): Whether to use the cached logger instance.
        """
        if use_loguru:
            # Use Loguru for logging
            self._set_loguru_logger(log_file, debug, verbose)
        else:
            # Use standard logging
            self._set_logging_logger(package, log_file, debug, verbose, cache)

    def _set_loguru_logger(
        self, log_file: str | Path, debug: bool, verbose: bool
    ) -> None:
        """
        Set up and return a configured Loguru logger instance.

        Args:
            log_file (str | Path): The path to the log file.
            debug (bool): Whether to enable debug-level logging.
            verbose (bool): Whether to enable verbose logging.
        """
        try:
            from loguru import logger as loguru_logger
        except ImportError:
            raise ImportError(
                "Loguru is not installed. Please install it with 'core-helpers[logging]'."
            )

        # Loguru configuration
        loguru_logger.remove()  # Remove default configuration
        loguru_log_level: str = "DEBUG" if debug else "INFO"

        # Configure Loguru to log to file
        loguru_logger.add(
            log_file, level=loguru_log_level, format="{time} {level} {message}"
        )

        if verbose:
            # Configure Loguru to log to console
            loguru_logger.add(
                lambda msg: print(msg, end=""), level=loguru_log_level, colorize=True
            )

        self._logger = loguru_logger

    def _set_logging_logger(
        self,
        package: str,
        log_file: str | Path,
        debug: bool,
        verbose: bool,
        cache: bool,
    ) -> None:
        """
        Set up and return a configured standard logging logger instance.

        Args:
            package (str): The name of the package or project.
            log_file (str | Path): The path to the log file.
            debug (bool): Whether to enable debug-level logging.
            verbose (bool): Whether to enable verbose logging.
            cache (bool): Whether to use the cached logger instance.
        """
        # Standard logging configuration
        logger: logging.Logger = logging.getLogger(name=package)
        logger.propagate = False  # Prevent propagation to root logger

        if logger.hasHandlers() and not cache:
            # Remove existing handlers
            logger.handlers.clear()

        if not logger.hasHandlers():  # Prevent adding handlers multiple times
            # Define log handlers
            log_handlers = [logging.FileHandler(filename=log_file)]
            if verbose:
                log_handlers.append(logging.StreamHandler())

            # Set the log level and message format
            log_level: int = logging.DEBUG if debug else logging.INFO
            log_format = "[%(asctime)s] %(levelname)s: %(message)s"

            # If in debug mode, include additional information
            if debug:
                log_format += ": %(pathname)s:%(lineno)d in %(funcName)s"

            formatter = logging.Formatter(log_format)

            # Set the log level
            logger.setLevel(log_level)

            # Add handlers to the logger
            for handler in log_handlers:
                handler.setFormatter(formatter)
                handler.setLevel(log_level)
                logger.addHandler(handler)

        self._logger = logger

    def __getattr__(self, name: str):
        """
        Proxy attribute access to the underlying logger.

        Args:
            name (str): The name of the attribute to access.

        Raises:
            RuntimeError: If the logger has not been initialized.
        """
        if self._logger is None:
            raise RuntimeError(
                f"logging.Logger accessed before initialization: tried to use '{name}'"
            )
        return getattr(self._logger, name)


# Create a shared proxy
logger: LoggerProxy = LoggerProxy()
