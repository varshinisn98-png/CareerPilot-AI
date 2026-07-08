from loguru import logger
import sys

# Remove default handler
logger.remove()

# Console handler
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="DEBUG",
)

# File handler
logger.add(
    "logs/careerpilot.log",
    rotation="10 MB",
    retention="10 days",
    compression="zip",
    level="INFO",
)

__all__ = ["logger"]
