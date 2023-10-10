from datetime import datetime

from loguru import logger
from create_bot import dp, logging
from aiogram.utils import executor


from pkg.db import create_database
from utils.set_bot_commands import set_default_commands
from handlers import rules


@logger.catch
async def on_startup(_):
    await create_database()
    await set_default_commands(dp)


executor.start_polling(dp, on_startup=on_startup)