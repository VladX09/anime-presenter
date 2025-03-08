import sys

from loguru import logger

log_msg_format = (
    "{time:YYYY-MM-DD HH:mm:ss} | <level>{level}</level>"
    " | <c>{name}</c>:<c>{function}</c>:<c>{line}</c> - <level>{message}</level>"
)

logger.remove(0)  # Remove default stderr handler to prevent output doubling
logger.add(sys.stdout, format=log_msg_format, level="DEBUG")
logger.disable("anime_presenter")
