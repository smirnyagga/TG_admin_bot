from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove
from loguru import logger

from keyboard.default.keyboards import DepartmentsKeyboard
from keyboard.default.pagination import Pagination, InlineKeyboardButton
from create_bot import dp, bot
from pkg.db.user_func import get_users_from_department_name
from states.show_user_state import UserCardState
from utils.check_is_available import is_department_available
from utils.send_card import send_card
from utils.validations import Validations


@logger.catch
@dp.message_handler(commands='show_department_cards')
async def show_user_by_department_start(message: types.Message):
    logger.info(f'Команда {message.text} от @{message.from_user.username} (id: {message.from_user.id})')
    if await Validations.moder_validation_for_supergroups(message):
        if await Validations.validation_for_moderator(message):
            text = 'Выберите отдел для вывода'
            await message.answer(text,
                                 reply_markup=await DepartmentsKeyboard.get_reply_keyboard(one_time=True))
            await UserCardState.show_departments.set()
        else:
            await message.answer('Вы не модератор')


@logger.catch
@dp.callback_query_handler(lambda call: True)
async def characters_page_callback(call, state: FSMContext):
    logger.info(f'Вывод пагинации для отделов '
                f'{call.message.text} от @{call.message.from_user.username} (id: {call.message.from_user.id})')
    page = int(call.data.split('#')[1])
    department_name = call.data.split('#')[0]
    await bot.delete_message(
        call.message.chat.id,
        call.message.message_id
    )
    await show_all(department_name, call.message, state=state, page=page)


@logger.catch
@dp.message_handler(state=UserCardState.show_departments)
async def show_users_by_department(message: types.Message, state: FSMContext, page=1):
    logger.info(f'UserCardState.show_departments с содержимым {message.text}'
                f' от @{message.from_user.username} (id: {message.from_user.id})')
    department_name = message.text
    if not await Validations.is_command(department_name):
        if await is_department_available(department_name):
            await message.answer(text=f'Был выбран отдел {department_name}', reply_markup=ReplyKeyboardRemove())
            await show_all(department_name, message, state=state, page=page)
        else:
            await bot.send_message(message.chat.id, 'Такой отдел не найден.',
                                   reply_markup=ReplyKeyboardRemove())
            await state.finish()
    else:
        await message.answer('Вы ввели команду. Выберите, пожалуйста, отдел из клавиатуры'
                             ' или вернитесь на главную страницу')


@logger.catch
@dp.message_handler(state=UserCardState.show_all)
async def show_all(department_name, message: types.Message, state: FSMContext, page=1):
    logger.info(f'UserCardState.show_all с содержимым {message.text}'
                f' от @{message.from_user.username} (id: {message.from_user.id})')
    user_list = await get_users_from_department_name(department_name=department_name)
    if user_list:
        paginator = Pagination(
            len(user_list),
            current_page=page,
            data_pattern=f'{department_name}#{{page}}'
        )
        paginator.add_after(
            InlineKeyboardButton(
                'Вернуться на главную',
                callback_data='back'))
        await send_card(
            message.chat.id,
            user=user_list[page - 1],
            reply_markup=paginator.markup,
        )
    else:
        await message.answer('Никто не привязан к отделу',
                             reply_markup=ReplyKeyboardRemove())
    await state.finish()
