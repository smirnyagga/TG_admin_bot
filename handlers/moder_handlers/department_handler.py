from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove

from keyboard.default.keyboards import DepartmentCommandsKeyboard, StopBotKeyboard, DepartmentsKeyboard
from create_bot import dp
from pkg.db.department_func import *
from pkg.db.user_func import get_user_by_tg_id, update_user_department
from states.department_states import DepartmentStates
from utils.check_is_available import is_department_available
from utils.validations import Validations


@logger.catch
@dp.message_handler(commands='department')
async def start_handler(message: types.Message, state: FSMContext):
    logger.info(f'Команда {message.text} от @{message.from_user.username} (id: {message.from_user.id})')
    if await Validations.moder_validation_for_supergroups(message):
        if await Validations.validation_for_moderator(message):
    # try:
    #     user = await get_user_by_tg_id(message.from_user.id)
    #     if user.is_moderator:
            await message.answer('Что вы хотите сделать?',
                                 reply_markup=DepartmentCommandsKeyboard.get_reply_keyboard())
            await DepartmentStates.moderator_choice.set()
        else:
            await message.answer('Вы не модератор',
                                 reply_markup=ReplyKeyboardRemove())
            await state.finish()
    # except (TypeError, AttributeError):
    #     await message.answer('Вас нет в базе, пожалуйста пройдите регистрацию',
    #                          reply_markup=ReplyKeyboardRemove())
    #     await state.finish()


@logger.catch
@dp.message_handler(state=DepartmentStates.moderator_choice)
async def moderator_choice(message: types.Message, state: FSMContext):
    logger.info(f'DepartmentStates.moderator_choice с содержимым {message.text}'
                f' от @{message.from_user.username} (id: {message.from_user.id})')
    answer = message.text
    if answer == 'Создать новый отдел':
        await message.answer('Введите название отдела который хотите создать',
                             reply_markup=StopBotKeyboard.get_reply_keyboard())
        await DepartmentStates.new_department.set()
    elif answer == 'Удалить отдел':
        await message.answer('Введите название отдела который хотите удалить',
                             reply_markup=await DepartmentsKeyboard.get_reply_keyboard())
        await DepartmentStates.delete_department.set()
    elif answer == 'Сменить имя отдела':
        await message.answer('Введите название отдела который хотите поменять',
                             reply_markup=await DepartmentsKeyboard.get_reply_keyboard())
        await DepartmentStates.change_department_name_get_name.set()
    elif answer == 'Сменить/добавить тим лида отдела':
        await message.answer('Введите название отдела тим лидера которого вы хотите поменять',
                             reply_markup=await DepartmentsKeyboard.get_reply_keyboard())
        await DepartmentStates.change_team_lead_name_get_name.set()
    else:
        await message.answer(f'⚠️ {answer} неверный ответ.',
                             reply_markup=ReplyKeyboardRemove())
        await state.finish()


@logger.catch
@dp.message_handler(state=DepartmentStates.new_department)
async def new_department(message: types.Message, state: FSMContext):
    logger.info(f'DepartmentStates.new_department с содержимым {message.text}'
                f' от @{message.from_user.username} (id: {message.from_user.id})')
    department_name = message.text
    if await is_department_available(department_name):
        await message.answer(f'Отдел {department_name} уже существует')
        await state.finish()
    else:
        await add_new_department(department_name)
        await message.answer(f'Отдел {department_name} создан')
        await state.finish()


@logger.catch
@dp.message_handler(state=DepartmentStates.delete_department)
async def delete_department(message: types.Message, state: FSMContext):
    logger.info(f'DepartmentStates.delete_department с содержимым {message.text}'
                f' от @{message.from_user.username} (id: {message.from_user.id})')
    department_name = message.text
    if await is_department_available(department_name):
        await update_user_department(department_name, 'EmptyDepartment')
        await delete_department_by_name(department_name)
        await DepartmentsKeyboard.delete_department_button(department_name)
        await message.answer(f'Отдел {department_name} удален',
                             reply_markup=ReplyKeyboardRemove())
        await state.finish()
    else:
        await message.answer('Такого отдела нет',
                             reply_markup=ReplyKeyboardRemove())
        await state.finish()


@logger.catch
@dp.message_handler(state=DepartmentStates.change_department_name_get_name)
async def get_new_department_name(message: types.Message, state: FSMContext):
    logger.info(f'DepartmentStates.change_department_name_get_name с содержимым {message.text}'
                f' от @{message.from_user.username} (id: {message.from_user.id})')
    department_name = message.text
    if await is_department_available(department_name):
        await message.answer('Введите новое название отдела',
                             reply_markup=StopBotKeyboard.get_reply_keyboard())
        await state.update_data(old_name=department_name)
        await DepartmentStates.change_department_name.set()
    else:
        await message.answer('Такого отдела нет',
                             reply_markup=ReplyKeyboardRemove())
        await state.finish()


@logger.catch
@dp.message_handler(state=DepartmentStates.change_department_name)
async def change_department_name(message: types.Message, state: FSMContext):
    logger.info(f'DepartmentStates.change_department_name с содержимым {message.text}'
                f' от @{message.from_user.username} (id: {message.from_user.id})')
    old_name_dict = await state.get_data()
    old_name = old_name_dict.get('old_name', '')
    new_name = message.text
    await update_department_name(old_name, new_name)
    await DepartmentsKeyboard.delete_department_button(old_name)
    await message.answer(f'Отдел {old_name} переименован в {new_name}',
                         reply_markup=ReplyKeyboardRemove())
    await state.finish()


@logger.catch
@dp.message_handler(state=DepartmentStates.change_team_lead_name_get_name)
async def get_new_team_lead_name(message: types.Message, state: FSMContext):
    logger.info(f'DepartmentStates.change_team_lead_name_get_name с содержимым {message.text}'
                f' от @{message.from_user.username} (id: {message.from_user.id})')
    department_name = message.text
    if await is_department_available(department_name):
        await message.answer('Введите новое имя Тим лида отдела',
                             reply_markup=StopBotKeyboard.get_reply_keyboard())
        await state.update_data(department=department_name)
        await DepartmentStates.change_team_lead_name.set()
    else:
        await message.answer('Такого отдела нет',
                             reply_markup=ReplyKeyboardRemove())
        await state.finish()


@logger.catch
@dp.message_handler(state=DepartmentStates.change_team_lead_name)
async def change_team_lead_name(message: types.Message, state: FSMContext):
    logger.info(f'DepartmentStates.change_team_lead_name с содержимым {message.text}'
                f' от @{message.from_user.username} (id: {message.from_user.id})')
    department_name_dict = await state.get_data()
    department_name = department_name_dict.get('department', '')
    await attach_tl_to_department(department_name, message.text)
    await message.answer(f'К отделу {department_name} прикреплен Тим лид: {message.text}',
                         reply_markup=ReplyKeyboardRemove())
    await state.finish()
