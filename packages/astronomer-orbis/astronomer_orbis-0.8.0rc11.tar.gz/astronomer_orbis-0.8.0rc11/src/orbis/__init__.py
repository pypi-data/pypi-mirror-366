"""
Orbis package initialization.
Sets up early logging capability.
"""

from orbis.utils.logger import get_early_logger

# Initialize logging at import time with default log file
logger = get_early_logger()
