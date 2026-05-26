"""Configuração centralizada de logging. Autora: Nathalia Adriele"""

import sys
from loguru import logger

from src.config.settings import LOG_FILE, LOGS_DIR


def setup_logger() -> None:
    """Configura o logger com saída para arquivo e console."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    logger.remove()

    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
               "<level>{message}</level>",
        level="INFO",
        colorize=True,
    )

    logger.add(
        str(LOG_FILE),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
               "{name}:{function}:{line} | {message}",
        level="DEBUG",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        encoding="utf-8",
    )

    logger.info("Logger configurado com sucesso.")


setup_logger()
