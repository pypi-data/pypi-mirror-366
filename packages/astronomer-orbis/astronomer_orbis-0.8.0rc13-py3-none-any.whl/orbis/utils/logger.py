import logging
import os
import shutil
import tempfile
import threading
from pathlib import Path

__all__ = ["get_logger", "get_early_logger", "update_early_logger_level", "CustomLogger", "TempLogManager"]

# Module-level caches
_loggers: dict[str, logging.Logger] = {}
_early_logger: logging.Logger | None = None


class PILFilter(logging.Filter):
    def filter(self, record):
        return record.filename not in ["Image.py", "PngImagePlugin.py"]


class TempLogManager:
    """
    Manages temporary logging before the actual log file is created.
    Uses a proper singleton pattern with thread safety.
    """

    _instance = None
    _lock = threading.Lock()  # Thread safety for singleton creation

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:  # Double-check pattern
                    instance = super().__new__(cls)
                    instance._initialized = False
                    cls._instance = instance
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        with self._lock:
            if self._initialized:  # Double-check pattern
                return
            self._temp_dir = tempfile.mkdtemp(prefix="orbis_")
            self._temp_log_path = str(Path(self._temp_dir) / "orbis_temp.log")
            self._temp_handler = None
            self._log_format = "%(asctime)s [%(levelname)s] %(filename)s/%(funcName)s(%(lineno)s): %(message)s"
            self._log_level = logging.INFO
            self._initialized = True
            self._initialize()

    def _initialize(self):
        """Initialize temporary log file and handler in a unique temp directory."""
        # Create log file handler
        self._temp_handler = logging.FileHandler(self._temp_log_path)
        self._temp_handler.setFormatter(logging.Formatter(self._log_format))
        self._temp_handler.addFilter(PILFilter())

        # Initialize root logger with temp handler
        root_logger = logging.getLogger("root")
        root_logger.setLevel(self._log_level)

        # Remove existing handlers and add new one
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        root_logger.addHandler(self._temp_handler)
        root_logger.info("---Temporary logging initialized in %s---", self._temp_dir)

    def set_log_level(self, verbose: int = 0) -> None:
        """
        Set the log level based on verbosity.

        Args:
            verbose (int): Verbosity level (0-3) corresponding to CRITICAL, WARNING, INFO, DEBUG
        """
        log_levels = [logging.CRITICAL, logging.WARNING, logging.INFO, logging.DEBUG]
        log_level = log_levels[min(verbose, 3)]
        self._log_level = log_level
        root_logger = logging.getLogger("root")
        root_logger.setLevel(log_level)
        if self._temp_handler:
            self._temp_handler.setLevel(log_level)

    def transfer_logs(self, target_file: str) -> None:
        """
        Transfer logs from temporary file to target file.
        The temp file is kept in the temporary directory until cleanup.

        Args:
            target_file (str): Path to the target log file
        """
        if not os.path.exists(self._temp_log_path):
            return

        # Ensure target directory exists
        os.makedirs(os.path.dirname(target_file), exist_ok=True)

        # Copy temp file contents to target file
        shutil.copy2(self._temp_log_path, target_file)

        # Log the transfer
        logger = logging.getLogger("root")
        logger.info(f"Logs transferred to: {target_file}")

    def cleanup(self) -> None:
        """
        Remove handler and cleanup temporary directory.
        """
        if self._temp_handler:
            root_logger = logging.getLogger("root")
            root_logger.removeHandler(self._temp_handler)
            self._temp_handler.close()
            self._temp_handler = None

        # Remove temporary directory and all its contents
        if self._temp_dir and os.path.exists(self._temp_dir):
            try:
                shutil.rmtree(self._temp_dir)
                self._temp_dir = None
            except Exception as e:
                # Log but don't raise - this is cleanup code
                logging.getLogger("root").warning(f"Failed to cleanup temp directory: {e}")


class CustomLogger:
    """
    Custom Logger class to setup logger with file handler.
    """

    def __init__(self, name: str, log_file: str, log_level: str):
        self.name = name
        self.log_file = log_file
        self.log_level = log_level
        self.logger = self.setup_custom_logger()

    def setup_custom_logger(self) -> logging.Logger:
        """Custom logger setup

        Args:
            name (str): Name of the logger
            log_file (str): Log file path
            log_level (str): Log Level

        Returns:
            logging.Logger: Logger object
        """
        if not hasattr(CustomLogger, "_temp_manager"):
            CustomLogger._temp_manager = TempLogManager()

        logger = logging.getLogger(self.name)
        logger.setLevel(self.log_level)

        # Setup file handler
        log_format = "%(asctime)s [%(levelname)s] %(filename)s/%(funcName)s(%(lineno)s): %(message)s"
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(logging.Formatter(log_format))
        file_handler.addFilter(PILFilter())

        # Clear and add new handler
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        logger.addHandler(file_handler)
        logger.info("======== New Report Session Started ========")

        # Transfer temp logs after logger is ready
        CustomLogger._temp_manager.transfer_logs(self.log_file)

        return logger


def get_logger(name: str, log_file: str, verbose: int = 0) -> logging.Logger:
    global _loggers

    if name in _loggers:
        logger = _loggers[name]
        # Update path and level if needed
        if logger.handlers:
            handler = logger.handlers[0]
            if isinstance(handler, logging.FileHandler) and handler.baseFilename != log_file:
                handler.close()
                handler.baseFilename = log_file
                handler.stream = open(log_file, "a")
        return logger

    # Create new logger if doesn't exist
    log_levels = ["CRITICAL", "WARNING", "INFO", "DEBUG"]
    log_level = log_levels[min(verbose, 3)]
    custom_logger = CustomLogger(name, log_file, log_level)
    _loggers[name] = custom_logger.logger
    return custom_logger.logger


def get_early_logger() -> logging.Logger:
    """
    Get the root logger for early logging before file handler setup.
    This can be used anywhere in the code for early debugging.
    Logs will be written to a temporary file and kept for debugging.

    Returns:
        logging.Logger: The root logger configured with temporary file handler
    """
    global _early_logger
    # This will ensure the temp log manager is initialized and return the root logger
    if _early_logger is None:
        TempLogManager()
        _early_logger = logging.getLogger("root")
    return _early_logger


def update_early_logger_level(verbose: int = 3) -> None:
    """Update the logging level based on verbosity."""
    logger = logging.getLogger("root")
    if verbose >= 4:
        logger.setLevel(logging.DEBUG)
    temp_manager = TempLogManager()
    temp_manager.set_log_level(verbose)
