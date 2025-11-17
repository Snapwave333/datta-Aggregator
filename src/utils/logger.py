"""Logging configuration using loguru."""
import sys
from loguru import logger
from src.config import settings

# Remove default handler
logger.remove()

# Add console handler
logger.add(
    sys.stdout,
    level=settings.log_level,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
)

# Add file handler
logger.add(
    settings.log_file,
    level=settings.log_level,
    rotation="10 MB",
    retention="30 days",
    compression="gz",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
)


def get_logger(name: str):
    """Get a logger instance with the given name."""
    return logger.bind(name=name)
