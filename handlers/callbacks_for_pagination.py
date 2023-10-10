from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove
from loguru import logger

from handlers.moder_handlers.moders_output import characters_page_callback
from create_bot import dp, bot
from pkg.db.user_func import delete_user_by_tg_id, update_user_approve
from pkg.settings import settings
from utils.delete_user import delete_user


@logger.catch
@dp.callback_query_handler(lambda call: call.data.split('#')[0] == 'approve')
async def callback_approve(call):
    moder_tg = call['from']['username']
    _, page, telegram_id, user_name = call.data.split('#')
    logger.info(f'Карточка {user_name} одобрена модератором @{moder_tg}')
    await update_user_approve(int(telegram_id))
    await bot.send_message(chat_id=settings.TELEGRAM_MODERS_CHAT_ID,
                           text=f'Пользователь {user_name} добавлен модератором @{moder_tg}')
    await bot.send_message(telegram_id, text='Анкета обновлена, проверьте состояние')
    if page == '0':
        await bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                            message_id=call.message.message_id,
                                            reply_markup=None)
    else:
        await characters_page_callback(call)


@logger.catch
@dp.callback_query_handler(lambda call: call.data.split('#')[0] == 'refilling')
async def callback_refilling(call):
    moder_tg = call['from']['username']
    _, page, telegram_id, user_name = call.data.split('#')
    logger.info(f'Карточка {user_name} отправлена на перезаполнение модератором @{moder_tg}')
    await delete_user_by_tg_id(int(telegram_id))
    await bot.send_message(chat_id=settings.TELEGRAM_MODERS_CHAT_ID,
                           text=f'Пользователь {user_name} отправлен на перезаполнение модератором @{moder_tg}')
    await bot.send_message(telegram_id, text='Анкета обновлена, проверьте состояние')
    if page == '0':
        await bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                            message_id=call.message.message_id,
                                            reply_markup=None)
    else:
        await characters_page_callback(call)


@logger.catch
@dp.callback_query_handler(lambda call: call.data.split('#')[0] == 'delete_user')
async def callback_delete_user(call):
    channels = settings.TELEGRAM_SCHOOL_CHATS
    moder_tg = call['from']['username']
    _, page, telegram_id, user_name = call.data.split('#')
    logger.info(f'Карточка {user_name} удалена модератором @{moder_tg}')
    await delete_user_by_tg_id(int(telegram_id))
    await bot.send_message(chat_id=settings.TELEGRAM_MODERS_CHAT_ID,
                           text=f'Пользователь {user_name} удален модератором @{moder_tg}')
    await delete_user(int(telegram_id), channels)
    await bot.send_message(telegram_id, text='Анкета обновлена, проверьте состояние')
    if page == '0':
        await bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                            message_id=call.message.message_id,
                                            reply_markup=None)
    else:
        await characters_page_callback(call)


@logger.catch
@dp.callback_query_handler(lambda call: call.data.split('#')[0] == 'back')
async def callback_back(call, state: FSMContext):
    logger.info(f'Возврат на главную в меню модерации карточки @{call.message.chat.username}')
    await bot.send_message(call.message.chat.id, 'Возвращаю на главную',
                           reply_markup=ReplyKeyboardRemove())
    await bot.delete_message(
        call.message.chat.id,
        call.message.message_id
    )
    await state.finish()
