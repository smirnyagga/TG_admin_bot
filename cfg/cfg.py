# -*- coding: utf-8 -*-
import os

from envreader import EnvMissingError
from envreader import EnvReader
from envreader import EnvTransformError
from envreader import Field


class Config(EnvReader):
    # SQLITE_FILENAME: str = Field('blah.db', description="sqlite3 database file path")
    SECRET_KEY: str = Field(..., description="Admin Bot Secret Key")
    TELEGRAM_MODERS_CHAT_ID: int = Field(..., description="Moders_IDs")
    TELEGRAM_SCHOOL_CHATS: list = Field(..., description="School_Chat_ID")

    POSTGRES_HOSTNAME: str = Field(..., description='hostname')
    POSTGRES_DATABASE: str = Field(..., description='db_name')
    POSTGRES_USER: str = Field(..., description='user_name')
    POSTGRES_PASSWORD: str = Field(..., description='password')
    POSTGRES_PORT: int = Field(..., description='port_number')
    SQLITE_FILENAME: str = Field('blah.db', description="sqlite3 database file path")
# class Config():
#     SECRET_KEY = os.getenv('SECRET_KEY')
#     TELEGRAM_MODERS_CHAT_ID = os.getenv('TELEGRAM_MODERS_CHAT_ID')
#     TELEGRAM_SCHOOL_CHATS = os.getenv('TELEGRAM_SCHOOL_CHATS')
#
#     POSTGRES_HOSTNAME = os.getenv('POSTGRES_HOSTNAME')
#     POSTGRES_DATABASE = os.getenv('POSTGRES_DATABASE')
#     POSTGRES_USER = os.getenv('POSTGRES_USER')
#     POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
#     POSTGRES_PORT = os.getenv('POSTGRES_PORT')


try:
    config = Config()

except EnvTransformError as e:
    print('Malformed environment parameter {}!'.format(e.field))
    print('Settings help:\n' + Config(populate=False).help())
    print('Committing suicide...')

except EnvMissingError as e:
    print('Configuration key {} was not found in env!'.format(e.args[0]))
    print('Settings help:\n' + Config(populate=False).help())
    print('Committing suicide...')
