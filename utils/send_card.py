from aiogram.types import ReplyKeyboardRemove
from aiogram.utils.exceptions import BadRequest
from loguru import logger

from create_bot import bot
from pkg.db.models.user import User


@logger.catch
async def send_card(chat_id: int, user: User, reply_markup=ReplyKeyboardRemove()) -> None:
    logger.info(f'Отправка неполной карточки в чат {chat_id}')
    caption = f'ФИО: {user.surname} {user.name} {user.patronymic}\n' \
              f'Пол: {user.gender}\n' \
              f'Логин в Telegram: {user.tg_login}\n' \
              f'Желаемый отдел: {user.desired_department}\n' \
              f'Скилы: {user.skills}\n' \
              f'Курсы: {user.education}\n' \
              f'Время в неделю для работы над проектом: {user.time_for_work}\n' \
              f'Желание участвовать в управлении: {user.management_wish}\n' \
              f'Город: {user.city}\n' \
              f'Откуда узнал о школе: {user.source_of_knowledge}\n' \
              f'Комментарий тимлида: {user.lead_description}\n' \
              f'Время присоединения: {user.join_time}\n'
    if user.is_approved == 1:
        caption += '\nАнкета проверена\n'
    if user.is_moderator == 1:
        caption += 'Модератор\n'
    try:
        await bot.send_photo(chat_id, user.photo, caption=caption,
                             reply_markup=reply_markup)
    except BadRequest:
        await bot.send_message(chat_id, caption + '\nФото отсутствует в бд',
                               reply_markup=reply_markup)


@logger.catch
async def send_full_card(chat_id: int, user: User, reply_markup=ReplyKeyboardRemove()) -> None:
    logger.info(f'Отправка полной карточки в чат {chat_id}')
    caption = f'Системная информация:\n\n'\
                                                \
              f'ID: {user.user_id}\n' \
              f'TG ID: {user.telegram_id}\n' \
              f'Почта: {user.email}\n' \
              f'Git или Behance: {user.git}{user.behance}\n\n' \
                                                                      \
              f'Общая информация:\n\n' \
                                              \
              f'ФИО: {user.surname} {user.name} {user.patronymic}\n' \
              f'Пол: {user.gender}\n' \
              f'Логин в Telegram: {user.tg_login}\n' \
              f'Желаемый отдел: {user.desired_department}\n' \
              f'Скилы: {user.skills}\n' \
              f'Курсы: {user.education}\n' \
              f'Время в неделю для работы над проектом: {user.time_for_work}\n' \
              f'Желание участвовать в управлении: {user.management_wish}\n' \
              f'Город: {user.city}\n' \
              f'Откуда узнал о школе: {user.source_of_knowledge}\n' \
              f'Комментарий тимлида: {user.lead_description}\n' \
              f'Время присоединения: {user.join_time}\n'
    if user.is_approved == 1:
        caption += f'\nАнкета проверена\n'
    if user.is_moderator == 1:
        caption += f'Модератор\n'
    try:
        await bot.send_photo(chat_id, user.photo, caption=caption,
                             reply_markup=reply_markup)
    except BadRequest:
        await bot.send_message(chat_id, caption + f'\nФото отсутствует в бд',
                               reply_markup=reply_markup)


@logger.catch
async def send_short_card(chat_id: int, user: User, reply_markup=ReplyKeyboardRemove()) -> None:
    logger.info(f'Отправка урезанной карточки (из /blind_change) в чат {chat_id}')
    caption = f'Краткая информация:\n\n'\
                                                \
              f'ID: {user.user_id}\n' \
              f'TG ID: {user.telegram_id}\n' \
              f'TG Tag {user.tg_login}\n' \
              f'ФИО: {user.surname} {user.name} {user.patronymic}'

    try:
        await bot.send_message(chat_id=chat_id, text=caption, reply_markup=reply_markup)
    except BadRequest:
        await bot.send_message(chat_id=chat_id, text='Техническая ошибка с карточкой', reply_markup=reply_markup)
