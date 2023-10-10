import imghdr
import os
import time

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove, ContentType
from loguru import logger

from keyboard.default.inline_keyboards import BackInlineKeyboard, ModeratorChangeCardInlineKeyboard
from keyboard.default.keyboards import StopBotKeyboard, DepartmentsKeyboard
from keyboard.default.pagination import Pagination, InlineKeyboardButton
from create_bot import dp, bot
from pkg.db.user_func import get_user_by_tg_id, get_all_users, update_field_value, delete_user_by_tg_id
from pkg.settings import settings
from utils import validations
from utils.config_utils import ConfigUtils
from utils.context_helper import ContextHelper
from utils.delete_user import delete_user
from utils.send_card import send_full_card
from utils.validations import Validations


@logger.catch
@dp.message_handler(commands='change_card_by_moder')
async def change_card_by_moder(message: types.Message, state: FSMContext):
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
    logger.info(f'\tОтправка карточки для изменения (от модера) с содержимым {message.text}'
                f' от @{message.from_user.username} (id: {message.from_user.id})')
    user_list = await get_all_users()
    if user_list:
        paginator = Pagination(
            len(user_list),
            current_page=page,
            data_pattern='user_for_change#{page}'
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
        await send_full_card(
            message.chat.id,
            user=user_list[page - 1],
            reply_markup=paginator.markup,
        )
    else:
        await message.answer('Пользователей нет в базе данных', reply_markup=ReplyKeyboardRemove())


@logger.catch
@dp.callback_query_handler(lambda call: call.data.split('#')[0] == 'change_by_moder')
async def characters_for_edit_page_callback(call: types.CallbackQuery, state: FSMContext):
    logger.info(f'\t\tОтправка карточки для изменения (от модера) с содержимым {call.message.text}'
                f' от @{call.message.from_user.username} (id: {call.message.from_user.id})')
    _, page, field_name, telegram_id = call.data.split('#')
    await bot.delete_message(
        call.message.chat.id,
        call.message.message_id
    )
    user = await get_user_by_tg_id(int(telegram_id))
    await ContextHelper.add_user(user=user, context=state)
    await ContextHelper.add_some_data(data=field_name, context=state)
    text = f'Выбрано поле {field_name}. Введите, пожалуйста,' \
           f' значение, на которое хотите изменить данные'
    reply_markup = StopBotKeyboard.get_reply_keyboard()
    if field_name == 'desired_department':
        text = f'Выбрано поле {field_name}. Выберите, пожалуйста,' \
               f' отдел, на который хотите изменить'
        reply_markup = await DepartmentsKeyboard.get_reply_keyboard()
    elif field_name == 'photo':
        text = f'Выбрано изменение фото. Пожалуйста, отправьте фото'
    await bot.send_message(chat_id=call.message.chat.id,
                           text=text,
                           reply_markup=reply_markup)
    await state.set_state('change_by_moder')


@logger.catch
@dp.callback_query_handler(lambda call: call.data.split('#')[0] == 'user_for_change')
async def characters_page_callback(call):
    logger.info(f'Отправка карточки для изменения (от модера) с содержимым {call.message.text}'
                f' от @{call.message.from_user.username} (id: {call.message.from_user.id})')
    page = int(call.data.split('#')[1])
    await bot.delete_message(
        call.message.chat.id,
        call.message.message_id
    )
    await send_character_page_for_edit(call.message, page)


@logger.catch
@dp.message_handler(state='change_by_moder',
                    content_types=[ContentType.TEXT, ContentType.PHOTO, ContentType.DOCUMENT])
async def change_data_of_user(message: types.Message, state: FSMContext):
    logger.info(f'Отправка карточки для изменения (от модера) с содержимым {message.text}'
                f' от @{message.from_user.username} (id: {message.from_user.id})')
    user = await ContextHelper.get_user(state)
    field_name = await ContextHelper.get_some_data(state)
    moder_tg = message['from']['username']
    if field_name == 'photo':
        if message.content_type == ContentType.TEXT:
            await message.reply(text='Пожалуйста, отправьте фото', reply_markup=StopBotKeyboard().get_reply_keyboard())
            await state.set_state('change_by_moder')
        else:
            timestamp = str(time.time()).replace('.', '')
            file_name = f'photo_{timestamp}.jpg'
            file_path = os.path.join(ConfigUtils.get_temp_path(), file_name)
            if not message.content_type == 'photo':
                file = await bot.get_file(message.document.file_id)
                await bot.download_file(file.file_path, file_path)
            else:
                await message.photo[-1].download(destination_file=file_path)
            with open(file_path, 'rb') as file:
                if not imghdr.what(file):
                    await message.reply('Пожалуйста, отправьте изображение',
                                        reply_markup=StopBotKeyboard.get_reply_keyboard())
                    await state.set_state('change_by_moder')
                else:
                    answer = file_name
                    await bot.send_photo(photo=file,
                                         chat_id=settings.TELEGRAM_MODERS_CHAT_ID,
                                         caption=f'@{moder_tg} обновил фото {user.tg_login}')
                    await state.finish()
    else:
        answer = message.text
        if not await validations.Validations(field_name, message).validate_tg_login_email_git():
            await state.set_state('change_by_moder')
        else:
            await update_field_value(telegram_id=int(user.telegram_id), field=field_name, value=answer)
            await bot.send_message(chat_id=message.chat.id,
                                   text=f'Поле {field_name} теперь имеет значение: {answer}')
            await state.finish()


@logger.catch
@dp.callback_query_handler(lambda call: call.data.split('#')[0] == 'delete_user_by_menu')
async def callback_delete_user(call):
    logger.info(f'Удаление юзера через /change_card_by_moder (от модера) с содержимым {call.message.text}'
                f' от @{call.message.from_user.username} (id: {call.message.from_user.id})')
    channels = settings.TELEGRAM_SCHOOL_CHATS
    moder_tg = call['from']['username']
    _, page, telegram_id, user_name = call.data.split('#')

    await delete_user_by_tg_id(telegram_id)
    await bot.send_message(chat_id=settings.TELEGRAM_MODERS_CHAT_ID,
                           text=f'Пользователь {user_name} удален модератором @{moder_tg} вручную')
    await delete_user(telegram_id, channels)
    await bot.send_message(telegram_id, text='Ваша карточка была удалена. Свяжитесь с администратором')
    if page == '0':
        await bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                            message_id=call.message.message_id,
                                            reply_markup=None)
    else:
        await send_character_page_for_edit(call.message)
