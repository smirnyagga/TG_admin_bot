from aiogram.dispatcher import FSMContext
from loguru import logger

from utils.validations import Validations
from create_bot import dp
from aiogram.dispatcher.filters.builtin import CommandHelp
from aiogram import types


@logger.catch
@dp.message_handler(CommandHelp())
async def start_handler(message: types.Message, state: FSMContext):
    logger.info(f'Команда {message.text} от @{message.from_user.username} (id: {message.from_user.id})')
    if await Validations.moder_validation_for_supergroups(message):
        command_bot = 'Общие команды:\n\n' \
                      '/start - начать работу с ботом.\n\n' \
                      '/help - помощь по командам взаимодействия с ботом.\n\n' \
                      '/show_card - посмотреть личные карточки студентов Школы IT.\n\n' \
                      '/show_department_cards - показать карточки пользователей отдела.\n\n' \
                      '/change_card - изменение данных в своей карточке.\n\n' \
                      '/moder - меню модератора.\n\n' \
                      '/rules - правила Школы IT.\n\n\n'
        await message.answer(command_bot)
        await state.finish()
