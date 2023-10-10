from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove

from keyboard.default.keyboards import ProjectCommandsKeyboard, StopBotKeyboard, ProjectKeyboard
from create_bot import dp
from pkg.db.project_func import *
from pkg.db.user_func import get_user_by_tg_id
from states.project_states import ProjectStates
from utils.check_is_available import is_project_available
from utils.validations import Validations


@logger.catch
@dp.message_handler(commands='project')
async def start_handler(message: types.Message, state: FSMContext):
    logger.info(f'Команда {message.text}'
                f' от @{message.from_user.username} (id: {message.from_user.id})')
    if await Validations.moder_validation_for_supergroups(message):
        if await Validations.validation_for_moderator(message):
            # try:
            #     user = await get_user_by_tg_id(message.from_user.id)
            #     if user.is_moderator:
            await message.answer('Что вы хотите сделать?',
                                 reply_markup=ProjectCommandsKeyboard.get_reply_keyboard())
            await ProjectStates.moderator_choice.set()
        else:
            await message.answer('Вы не модератор',
                                 reply_markup=ReplyKeyboardRemove())
            await state.finish()
        # except (TypeError, AttributeError):
        #     await message.answer('Вас нет в базе, пожалуйста пройдите регистрацию',
        #                          reply_markup=ReplyKeyboardRemove())
        #     await state.finish()


@logger.catch
@dp.message_handler(state=ProjectStates.moderator_choice)
async def moderator_choice(message: types.Message, state: FSMContext):
    logger.info(f'ProjectStates.moderator_choice с содержимым {message.text}'
                f' от @{message.from_user.username} (id: {message.from_user.id})')
    answer = message.text
    if answer == ProjectCommandsKeyboard.A_CREATE_PROJECT:
        await message.answer('Введите название проекта который хотите создать',
                             reply_markup=StopBotKeyboard.get_reply_keyboard())
        await ProjectStates.new_project.set()
    elif answer == ProjectCommandsKeyboard.B_DELETE_PROJECT:
        await message.answer('Введите название проекта который хотите удалить',
                             reply_markup=await ProjectKeyboard.get_reply_keyboard())
        await ProjectStates.delete_project.set()
    elif answer == ProjectCommandsKeyboard.C_CHANGE_PROJECT_NAME:
        await message.answer('Введите название проекта который хотите поменять',
                             reply_markup=await ProjectKeyboard.get_reply_keyboard())
        await ProjectStates.change_project_name_get_name.set()
    elif answer == ProjectCommandsKeyboard.D_CHANGE_PROJECT_LEAD:
        await message.answer('Введите название проекта тим лидера которого вы хотите поменять',
                             reply_markup=await ProjectKeyboard.get_reply_keyboard())
        await ProjectStates.change_team_lead_name_get_name.set()
    else:
        await message.answer(f'⚠️ {answer} неверный ответ.',
                             reply_markup=ReplyKeyboardRemove())
        await state.finish()


@logger.catch
@dp.message_handler(state=ProjectStates.new_project)
async def new_project(message: types.Message, state: FSMContext):
    logger.info(f'ProjectStates.new_project с содержимым {message.text}'
                f' от @{message.from_user.username} (id: {message.from_user.id})')
    project_name = message.text
    if await is_project_available(project_name):
        await message.answer(f'Отдел {project_name} уже существует')
        await state.finish()
    else:
        await add_new_project(project_name)
        await message.answer(f'Проект "{project_name}" создан')
        await state.finish()


@logger.catch
@dp.message_handler(state=ProjectStates.delete_project)
async def delete_project(message: types.Message, state: FSMContext):
    logger.info(f'ProjectStates.delete_project с содержимым {message.text}'
                f' от @{message.from_user.username} (id: {message.from_user.id})')
    project_name = message.text
    if await is_project_available(project_name):
        await delete_project_by_name(project_name)
        await ProjectKeyboard.delete_project_button(project_name)
        await message.answer(f'Проект "{project_name}" удален',
                             reply_markup=ReplyKeyboardRemove())
        await state.finish()
    else:
        await message.answer('Такого проекта нет',
                             reply_markup=ReplyKeyboardRemove())
        await state.finish()


@logger.catch
@dp.message_handler(state=ProjectStates.change_project_name_get_name)
async def get_new_project_name(message: types.Message, state: FSMContext):
    logger.info(f'ProjectStates.change_project_name_get_name с содержимым {message.text}'
                f' от @{message.from_user.username} (id: {message.from_user.id})')
    project_name = message.text
    if await is_project_available(project_name):
        await message.answer('Введите новое название проекта',
                             reply_markup=StopBotKeyboard.get_reply_keyboard())
        await state.update_data(old_name=project_name)
        await ProjectStates.change_project_name.set()
    else:
        await message.answer('Такого проекта нет',
                             reply_markup=ReplyKeyboardRemove())
        await state.finish()


@logger.catch
@dp.message_handler(state=ProjectStates.change_project_name)
async def change_project_name(message: types.Message, state: FSMContext):
    logger.info(f'ProjectStates.change_project_name с содержимым {message.text}'
                f' от @{message.from_user.username} (id: {message.from_user.id})')
    old_name_dict = await state.get_data()
    old_name = old_name_dict.get('old_name', '')
    new_name = message.text
    await update_project_name(old_name, new_name)
    await ProjectKeyboard.delete_project_button(old_name)
    await message.answer(f'Проект "{old_name}" переименован в "{new_name}"',
                         reply_markup=ReplyKeyboardRemove())
    await state.finish()


@logger.catch
@dp.message_handler(state=ProjectStates.change_team_lead_name_get_name)
async def get_new_team_lead_name(message: types.Message, state: FSMContext):
    logger.info(f'ProjectStates.change_team_lead_name_get_name с содержимым {message.text}'
                f' от @{message.from_user.username} (id: {message.from_user.id})')
    project_name = message.text
    if await is_project_available(project_name):
        await message.answer('Введите новое имя Тим лида проекта',
                             reply_markup=StopBotKeyboard.get_reply_keyboard())
        await state.update_data(department=project_name)
        await ProjectStates.change_team_lead_name.set()
    else:
        await message.answer('Такого проекта нет',
                             reply_markup=ReplyKeyboardRemove())
        await state.finish()


@logger.catch
@dp.message_handler(state=ProjectStates.change_team_lead_name)
async def change_team_lead_name(message: types.Message, state: FSMContext):
    logger.info(f'ProjectStates.change_team_lead_name с содержимым {message.text}'
                f' от @{message.from_user.username} (id: {message.from_user.id})')
    project_name_dict = await state.get_data()
    project_name = project_name_dict.get('department', '')
    await attach_tl_to_project(project_name, message.text)
    await message.answer(f'К проекту "{project_name}" прикреплен Тим лид: "{message.text}"',
                         reply_markup=ReplyKeyboardRemove())
    await state.finish()
