"""Logging configuration for knowlithic LiveKit plugin."""

import logging
import sys
from typing import Optional

def setup_logging(
    level: int = logging.INFO,
    format_string: Optional[str] = None,
    stream: Optional[logging.StreamHandler] = None
) -> logging.Logger:
    """Setup logging for the knowlithic plugin."""
    
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    if stream is None:
        stream = logging.StreamHandler(sys.stdout)
    
    logger = logging.getLogger("livekit.plugins.knowlithic")
    logger.setLevel(level)
    
    # Avoid adding handlers multiple times
    if not logger.handlers:
        formatter = logging.Formatter(format_string)
        stream.setFormatter(formatter)
        logger.addHandler(stream)
    
    return logger

# Create default logger instance
logger = setup_logging()
