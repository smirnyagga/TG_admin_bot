import pydantic
from loguru import logger

from cfg.cfg import config as cfg


# class _Settings(pydantic.settings.BaseSettings):
#     class Config:
#         env_file_encoding = "utf-8"


class Settings:
    # PostgresQL
    POSTGRES_HOSTNAME: str = cfg.POSTGRES_HOSTNAME
    POSTGRES_DATABASE: str = cfg.POSTGRES_DATABASE
    POSTGRES_USER: str = cfg.POSTGRES_USER
    POSTGRES_PASSWORD: str = cfg.POSTGRES_PASSWORD
    POSTGRES_PORT: int = cfg.POSTGRES_PORT

    # BaseSettings
    # SQLITE_FILENAME: str = cfg.SQLITE_FILENAME
    SECRET_KEY: str = cfg.SECRET_KEY
    TELEGRAM_MODERS_CHAT_ID: int = cfg.TELEGRAM_MODERS_CHAT_ID
    TELEGRAM_SCHOOL_CHATS: list = cfg.TELEGRAM_SCHOOL_CHATS


@logger.catch
def _get_settings() -> Settings:
    logger.info('Получение конфига')
    settings = Settings()
    return settings

