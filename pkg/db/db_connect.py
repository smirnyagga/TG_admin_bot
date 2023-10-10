from contextlib import asynccontextmanager

import asyncpg
from loguru import logger

from pkg.settings import settings


@asynccontextmanager
@logger.catch
async def connect_to_db():
    logger.info('Коннет к БД')
    try:
        conn = await asyncpg.connect(
            host=settings.POSTGRES_HOSTNAME,
            database=settings.POSTGRES_DATABASE,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            port=settings.POSTGRES_PORT)

        yield conn
        await conn.close()

    except Exception as ex:
        raise ex
