from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove
from loguru import logger

from keyboard.default.inline_keyboards import ModeratorChangeCardInlineKeyboard, BackInlineKeyboard
from keyboard.default.pagination import Pagination, InlineKeyboardButton
from create_bot import dp, bot
from pkg.db.user_func import get_user_by_tg_id, get_all_users
from utils.send_card import send_short_card
from utils.validations import Validations


@logger.catch
@dp.message_handler(commands='blind_change')
async def blind_change_card_by_moder(message: types.Message, state: FSMContext):
    logger.info(f'Команда {message.text} от @{message.from_user.username} (id: {message.from_user.id})')
    if await Validations.moder_validation_for_supergroups(message):
        if await Validations.validation_for_moderator(message):
    # try:
    #     user = await get_user_by_tg_id(message.from_user.id)
    #     if user.is_moderator:
            await send_character_page_for_edit(message)
        else:
            await message.answer('Вы не модератор',
                                 reply_markup=ReplyKeyboardRemove())
            await state.finish()
    # except (TypeError, AttributeError):
    #     await message.answer('Вас нет в базе, пожалуйста пройдите регистрацию',
    #                          reply_markup=ReplyKeyboardRemove())
    #     await state.finish()


@logger.catch
async def send_character_page_for_edit(message: types.Message, page=1):
    logger.info(f'Отправка "слепой" карточки с содержимым {message.text}'
                f' от @{message.from_user.username} (id: {message.from_user.id})')
    user_list = await get_all_users()
    if user_list:
        paginator = Pagination(
            len(user_list),
            current_page=page,
            data_pattern='user_for_change_short#{page}'
        )
        user = user_list[page - 1]
        list_of_buttons = ModeratorChangeCardInlineKeyboard(page, user, 'change_by_moder').\
            get_inline_keyboard(is_key=True)
        for buttons in list_of_buttons:
            paginator.add_before(
                *buttons)
        paginator.add_after(
            InlineKeyboardButton(text='Удалить',
                                 callback_data=f'delete_user_by_menu#{page}#{user.telegram_id}#{user.tg_login}')
        )
        paginator.add_after(
            *BackInlineKeyboard().get_inline_keyboard(is_key=True)
        )
        await send_short_card(
            message.chat.id,
            user=user_list[page - 1],
            reply_markup=paginator.markup,
        )
    else:
        await message.answer('Пользователей нет в базе данных', reply_markup=ReplyKeyboardRemove())


@logger.catch
@dp.callback_query_handler(lambda call: call.data.split('#')[0] == 'user_for_change_short')
async def characters_page_callback(call):
    logger.info(f'Отправка "слепой" карточки с содержимым {call.message.text}'
                f' от @{call.message.from_user.username} (id: {call.message.from_user.id})')
    page = int(call.data.split('#')[1])
    await bot.delete_message(
        call.message.chat.id,
        call.message.message_id
    )
    await send_character_page_for_edit(call.message, page)
