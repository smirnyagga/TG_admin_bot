from aiogram.utils.exceptions import NotEnoughRightsToRestrict, BadRequest
from loguru import logger

from pkg.db.user_func import delete_user_by_tg_id
from create_bot import bot


@logger.catch
async def delete_user(user_id, channels):
    logger.info(f'Кик юзера ({user_id}) из чатов школы')
    for channel in channels:
        try:
            await bot.kick_chat_member(chat_id=channel, user_id=user_id)
        except NotEnoughRightsToRestrict as e:
            print(e)
        except BadRequest as e:
            print(e)
    await delete_user_by_tg_id(telegram_id=user_id)
