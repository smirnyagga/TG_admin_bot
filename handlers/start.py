import asyncio
import imghdr
import os.path
import time
import validators

from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart, Text
from aiogram.dispatcher.storage import FSMContext
from aiogram.types import ReplyKeyboardRemove, ContentType

from create_bot import dp, bot
from handlers.rules import RULES
from keyboard.default.inline_keyboards import ModeratorSurveyInlineKeyboard
from keyboard.default.keyboards import *
from pkg.db.user_func import *
from pkg.settings import settings
from states.start_state import StartState
from utils.validations import Validations
from utils.config_utils import ConfigUtils
from utils.context_helper import ContextHelper
from utils.get_name import split_fullname
from utils.send_card import send_card, send_full_card
from utils.delete_user import delete_user


@logger.catch
@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    logger.info(f'Команда {message.text} от @{message.from_user.username} (id: {message.from_user.id})')
    if await Validations.moder_validation_for_supergroups(message):
        text = 'Привет!\n\n' \
               'Рады приветствовать Вас в Школе IT!\n\n' \
               'Школа IT Terra создана для помощи благотворительным фондам и людям.' \
               ' Каждый участник вносит вклад в общее дело. ' \
               'Школа – это комьюнити, которое помогает прокачивать навыки всем желающим. Мы учимся новому и всегда ' \
               'готовы помочь каждому участнику разобраться с возникшим вопросом.\n\n' \
               'Здесь собрались самые любознательные, целеустремленные и приветливые люди.' \
               ' Мы объединяем новичков и специалистов разных возрастов не только из разных городов России,' \
               ' но и мира.\n\n' \
               'Для того чтобы попасть в Школу, просим ответить на несколько вопросов'
        await message.answer(text, reply_markup=ChoiceKeyboard.get_reply_keyboard())
        await StartState.rules.set()


@logger.catch
@dp.message_handler(commands='moder')
async def moder_menu(message: types.Message, state: FSMContext):
    logger.info(f'Команда {message.text} от @{message.from_user.username} (id: {message.from_user.id})')
    if await Validations.moder_validation_for_supergroups(message):
        if await Validations.validation_for_moderator(message):
    # try:
    #     user = await get_user_by_tg_id(message.from_user.id)
    #     if user.is_moderator:
            commands_for_moder = 'Команды модераторов:\n\n' \
                                 '/department - добавить новый отдел или изменить данные о существующем.\n\n' \
                                 '/project -  добавить новый проект или изменить данные о существующем.\n\n' \
                                 '/review_cards - работа со всеми неапрувнутыми учениками.\n\n' \
                                 '/change_card_by_moder - изменение/удаление карточки учеников\n\n' \
                                 '/blind_change - изменение полей вслепую (когда карточка забагована)'
            await message.answer(text=commands_for_moder,
                                 reply_markup=StopBotKeyboard.get_reply_keyboard(add_stop=False))
            await state.finish()
        else:
            await message.answer('Вы не модератор',
                                 reply_markup=ReplyKeyboardRemove())
            await state.finish()
    # except (TypeError, AttributeError):
    #     await message.answer('Вас нет в базе, пожалуйста пройдите регистрацию',
    #                          reply_markup=ReplyKeyboardRemove())
    #     await state.finish()


@logger.catch
@dp.message_handler(commands='stop', state='*')
@dp.message_handler(Text(equals=ButtonFactory.get_stop_message()), state='*')
async def bot_stop(message: types.Message, state: FSMContext):
    logger.info(f'Команда /stop от @{message.from_user.username} (id: {message.from_user.id})')
    if await Validations.moder_validation_for_supergroups(message):
        text = 'Главная страница'
        await message.answer(text, reply_markup=types.ReplyKeyboardRemove())
        await state.finish()


@logger.catch
@dp.message_handler(commands='iammoder')
async def get_moder(message: types.Message):
    logger.info(f'Команда {message.text} от @{message.from_user.username} (id: {message.from_user.id})')
    if await Validations.moder_validation_for_supergroups(message):
        await message.answer('Введите ключ доступа', reply_markup=StopBotKeyboard.get_reply_keyboard())
        await StartState.get_moder.set()


@logger.catch
@dp.message_handler(state=StartState.rules_for_refilling)
async def get_rules(message: types.Message):
    logger.info(f'StartState.rules_for_refilling с содержимым: {message.text}'
                f' -> @{message.from_user.username} (id: {message.from_user.id})')
    text = 'Чтобы перезаполнить анкету, напомним правила :)'
    await message.answer(text, reply_markup=ChoiceKeyboard.get_reply_keyboard())
    await StartState.rules.set()


@logger.catch
@dp.message_handler(state=StartState.rules)
async def reading_rules(message: types.Message, state: FSMContext):
    logger.info(f'StartState.rules с содержимым: {message.text} '
                f'-> @{message.from_user.username} (id: {message.from_user.id})')
    answer = message.text
    if await Validations.is_command(answer):
        await message.answer('Вы ввели команду. Пожалуйста, выберите один из предложенных вариантов ответа',
                             reply_markup=ChoiceKeyboard.get_reply_keyboard())
    elif answer == ChoiceKeyboard.A_READ_RULES:
        await message.answer(RULES, reply_markup=ReplyKeyboardRemove())
        await message.answer('Вы согласны с правилами?', reply_markup=AgreementKeyboard.get_reply_keyboard())
        await StartState.rule_decision.set()
    elif answer == ChoiceKeyboard.B_DONT_READ_RULES:
        await message.answer(
            'Очень жаль, что наше с Вами общение подходит к концу 😔\nЕсли Вы передумаете, '
            'то я всегда тут! Нужно лишь повторно вызвать команду /start',
            reply_markup=ReplyKeyboardRemove())
        await state.reset_state()
    else:
        await message.answer('Ошибка ввода! ⛔ \nВыберите один из предложенных вариантов')
        await StartState.rules.set()


@logger.catch
@dp.message_handler(state=StartState.rule_decision)
async def decision_about_rules(message: types.Message, state: FSMContext):
    logger.info(f'StartState.rule_decision с содержимым: {message.text} '
                f'-> @{message.from_user.username} (id: {message.from_user.id})')
    answer = message.text
    if await Validations.is_command(answer):
        await message.answer('Вы ввели команду. Пожалуйста, выберите один из предложенных вариантов ответа',
                             reply_markup=ConfidentialKeyboard.get_reply_keyboard())
    elif answer == AgreementKeyboard.A_AGREE_WITH_RULES:
        # await message.answer('Перед тем как начать заполнять анкету, мы хотим сообщить, что Ваши анкетные данные будут'
        #                      ' хранится у этого бота, доступ к которым будет общим для всех желающих.\n\n'
        #                      'Мы понимаем, что для некоторых это может быть неприемлемо по личным соображениям.\n\n'
        #                      'Пожалуйста, подтвердите согласие на обработку персональных данных',
        #                      reply_markup=ConfidentialKeyboard.get_reply_keyboard())
        await message.answer('Перед тем как начать заполнять анкету, мы хотим сообщить, что Ваши анкетные данные будут'
                             ' хранится у этого бота, доступ к которым будет у модераторов школы.\n\n'
                             'Пожалуйста, подтвердите согласие на обработку персональных данных',
                             reply_markup=ConfidentialKeyboard.get_reply_keyboard())
        await StartState.confidential_decision.set()
    elif answer == AgreementKeyboard.B_DONT_AGREE_WITH_RULES:
        await message.answer('Жаль, что вас не устроили наши правила 😔\n'
                             'В любой момент, если передумаете, можете '
                             'попробовать снова, для этого нажмите команду /start',
                             reply_markup=ReplyKeyboardRemove())
        await state.reset_state()
    else:
        await message.answer('Ошибка ввода! ⛔ \nВыберите один из предложенных вариантов')
        await StartState.rule_decision.set()


@logger.catch
@dp.message_handler(state=StartState.confidential_decision)
async def confidential_decision(message: types.Message, state: FSMContext):
    logger.info(f'StartState.confidential_decision с содержимым: {message.text} '
                f'-> @{message.from_user.username} (id: {message.from_user.id})')
    answer = message.text
    if await Validations.is_command(answer):
        await message.answer('Вы ввели команду. Пожалуйста, выберите один из предложенных вариантов ответа',
                             reply_markup=AgreementKeyboard.get_reply_keyboard())
    elif answer == ConfidentialKeyboard.A_CONFIDENTIAL_AGREE:
        print(message.from_user.id)
        if await get_user_by_tg_id(tg_id=message.from_user.id) is None:
            await message.answer('Введите ваше ФИО 🖊',
                                 reply_markup=StopBotKeyboard.get_reply_keyboard())
            await StartState.gender.set()
        else:
            await message.answer('Вы уже зарегистрированы в системе. Хотите обновить данные?',
                                 reply_markup=YesNoKeyboard.get_reply_keyboard())
            await StartState.update_info.set()
    elif answer == ConfidentialKeyboard.B_CONFIDENTIAL_DISAGREE:
        await message.answer('Жаль, что Вы не согласны на обработку персональных данных.\n\n'
                             'Пожалуйста, свяжитесь с модератором для попытки альтернативного анкетирования.\n\n'
                             'В любой момент, если передумаете, можете '
                             'попробовать снова, для этого нажмите команду /start',
                             reply_markup=ReplyKeyboardRemove())
        await state.reset_state()
    else:
        await message.answer('Ошибка ввода! ⛔ \nВыберите один из предложенных вариантов')
        await StartState.confidential_decision.set()


@logger.catch
@dp.message_handler(state=StartState.update_info)
async def update_info(message: types.Message):
    logger.info(f'StartState.update_info с содержимым: {message.text} '
                f'-> @{message.from_user.username} (id: {message.from_user.id})')
    answer = message.text
    if await Validations.is_command(answer):
        await message.answer('Вы ввели команду. Пожалуйста, выберите один из предложенных вариантов ответа',
                             reply_markup=YesNoKeyboard.get_reply_keyboard())
    elif answer == YesNoKeyboard.A_YES:
        await message.answer('Введите ваше ФИО 🖊',
                             reply_markup=StopBotKeyboard.get_reply_keyboard())
        tg_id = message.from_user.id
        await delete_user_by_tg_id(telegram_id=tg_id)
        await StartState.gender.set()
    elif answer == YesNoKeyboard.B_NO:
        await message.answer('Хотите проверить Вашу анкету?',
                             reply_markup=YesNoKeyboard.get_reply_keyboard())
        await StartState.choice.set()


@logger.catch
@dp.message_handler(state=StartState.choice)
async def questionnaire_choice(message: types.Message, state: FSMContext):
    logger.info(f'StartState.choice с содержимым: {message.text} '
                f'-> @{message.from_user.username} (id: {message.from_user.id})')
    answer = message.text
    if await Validations.is_command(answer):
        await message.answer('Вы ввели команду. Пожалуйста, выберите один из предложенных вариантов ответа',
                             reply_markup=YesNoKeyboard.get_reply_keyboard())
    elif answer == YesNoKeyboard.A_YES:
        await message.answer('Для проверки нажмите на кнопку ниже',
                             reply_markup=CheckAccessKeyboard.get_reply_keyboard(add_stop=False))
        await StartState.check_questionnaire.set()
    elif answer == YesNoKeyboard.B_NO:
        await message.answer('Ок. Возвращаю Вас в начало',
                             reply_markup=ReplyKeyboardRemove())
        await state.reset_state()


@logger.catch
@dp.message_handler(state=StartState.gender)
async def get_user_gender(message: types.Message, state: FSMContext):
    logger.info(f'StartState.gender с содержимым: {message.text} '
                f'-> @{message.from_user.username} (id: {message.from_user.id})')
    answer = message.text
    if await Validations.is_command(answer):
        await message.answer('Вы ввели команду. Пожалуйста, введите ваше ФИО',
                             reply_markup=StopBotKeyboard.get_reply_keyboard())
    else:
        if len(answer.split(' ')) < 2:
            await message.answer('Пожалуйста, введите хотя бы фамилию и имя',
                                 reply_markup=StopBotKeyboard.get_reply_keyboard())
        else:
            surname, name, patronymic = split_fullname(answer)
            if name.isalpha():
                user = User()
                user.join_time = datetime.date.today()
                user.telegram_id = message.from_user.id
                user.tg_login = f'@{message.from_user.username}'
                user.surname, user.name, user.patronymic = surname, name, patronymic
                await add_new_user(user)
                await ContextHelper.add_user(user, state)
                await message.answer('Выберите Ваш пол',
                                     reply_markup=GenderKeyboard.get_reply_keyboard())
                await StartState.photo.set()
            else:
                await message.answer('Необходимо ввести ФИО\nПример: Иванов Иван Иванович\n'
                                     'Можно не указывать фамилию или отчество\nИмя указывать обязательно.')
                await StartState.gender.set()


@logger.catch
@dp.message_handler(state=StartState.photo)
async def ask_about_photo(message: types.Message, state: FSMContext):
    logger.info(f'StartState.photo с содержимым: {message.text} '
                f'-> @{message.from_user.username} (id: {message.from_user.id})')
    answer = message.text
    if await Validations.is_command(answer):
        await message.answer('Вы ввели команду. Пожалуйста, выберите один из предложенных вариантов ответа',
                             reply_markup=GenderKeyboard.get_reply_keyboard())
    else:
        user = await ContextHelper.get_user(state)
        if answer == GenderKeyboard.A_MALE_GENDER:
            user.gender = 'Мужской'
        elif answer == GenderKeyboard.B_FEMALE_GENDER:
            user.gender = 'Женский'
        else:
            await message.answer('Ошибка ввода! ⛔ \nВыберите один из предложенных вариантов')
            await StartState.photo.set()
            return
        await update_user_by_telegram_id(message.from_user.id, user)
        await ContextHelper.add_user(user, state)
        await message.answer('Хотите ли Вы загрузить свое фото?',
                             reply_markup=PhotoKeyboard.get_reply_keyboard())
        await StartState.decision_about_photo.set()


@logger.catch
@dp.message_handler(state=StartState.decision_about_photo)
async def decision_about_photo(message: types.Message):
    logger.info(f'StartState.decision_about_photo с содержимым: {message.text}'
                f' от @{message.from_user.username} (id: {message.from_user.id})')
    answer = message.text
    if await Validations.is_command(answer):
        await message.answer('Вы ввели команду. Пожалуйста, выберите один из предложенных вариантов ответа',
                             reply_markup=PhotoKeyboard.get_reply_keyboard())
    else:
        if answer == PhotoKeyboard.A_WANT_UPLOAD_PHOTO:
            await message.answer('Супер! Просто отправьте его мне.',
                                 reply_markup=StopBotKeyboard.get_reply_keyboard())
            await StartState.upload_photo.set()
        elif answer == PhotoKeyboard.B_DONT_WANT_UPLOAD_PHOTO:
            await message.answer('Хорошо, тогда продолжаем анкетирование 📝',
                                 reply_markup=StopBotKeyboard.get_reply_keyboard())
            await message.answer('Введите вашу почту для регистрации в Kaiten 📧')
            await StartState.gitlab.set()
        else:
            await message.answer('Ошибка ввода! ⛔ \nВыберите один из предложенных вариантов')
            await StartState.decision_about_photo.set()


@logger.catch
@dp.message_handler(state=StartState.upload_photo,
                    content_types=[ContentType.PHOTO, ContentType.DOCUMENT])
async def upload_photo(message: types.Message, state: FSMContext):
    logger.info(f'StartState.upload_photo с содержимым: {message.text}'
                f' от @{message.from_user.username} (id: {message.from_user.id})')
    timestamp = str(time.time()).replace('.', '')
    file_name = f'photo_{timestamp}.jpg'
    file_path = os.path.join(ConfigUtils.get_temp_path(), file_name)
    user = await ContextHelper.get_user(state)
    if not message.content_type == 'photo':
        file = await bot.get_file(message.document.file_id)
        await bot.download_file(file.file_path, file_path)
    else:
        await message.photo[-1].download(destination_file=file_path)
    with open(file_path, 'rb') as file:
        if not imghdr.what(file):
            await message.reply('Отправьте изображение.', reply_markup=StopBotKeyboard.get_reply_keyboard())
            await StartState.upload_photo.set()
        else:
            user.photo = file.read()
            await update_user_by_telegram_id(message.from_user.id, user)
            await ContextHelper.add_user(user, state)
            await message.answer('Спасибо!')
            await message.answer('Введите вашу почту 📧', reply_markup=StopBotKeyboard.get_reply_keyboard())
            await StartState.gitlab.set()
    if os.path.exists(file_path):
        os.remove(file_path)


@logger.catch
@dp.message_handler(state=StartState.gitlab)
async def get_gitlab(message: types.Message, state: FSMContext):
    logger.info(f'StartState.gitlab с содержимым: {message.text} '
                f'-> @{message.from_user.username} (id: {message.from_user.id})')
    answer = message.text
    if await Validations.is_command(answer):
        await message.answer('Вы ввели команду. Пожалуйста, введите вашу почту',
                             reply_markup=StopBotKeyboard.get_reply_keyboard())
    elif validators.email(answer):
        user = await ContextHelper.get_user(state)
        user.email = answer
        await update_user_by_telegram_id(message.from_user.id, user)
        await ContextHelper.add_user(user, state)
        await message.answer('Выберите, в какой бы отдел Вы хотели попасть?',
                             reply_markup=await DepartmentsKeyboard.get_reply_keyboard())
        await StartState.department.set()
    else:
        await message.answer('Вы ввели неверный формат почты',
                             reply_markup=StopBotKeyboard.get_reply_keyboard())


@logger.catch
@dp.message_handler(state=StartState.department)
async def get_department(message: types.Message, state: FSMContext):
    logger.info(f'StartState.department с содержимым: {message.text} '
                f'-> @{message.from_user.username} (id: {message.from_user.id})')
    answer = message.text
    if await Validations.is_command(answer):
        await message.answer('Вы ввели команду. Пожалуйста, введите или выберите желаемый отдел',
                             reply_markup=await DepartmentsKeyboard.get_reply_keyboard())
    elif answer == 'Design':
        user = await ContextHelper.get_user(state)
        user.desired_department = answer
        await update_user_by_telegram_id(message.from_user.id, user)
        await ContextHelper.add_user(user, state)
        await message.answer('Введите вашу ссылку на беханс 🌐',
                             reply_markup=StopBotKeyboard.get_reply_keyboard())
        await StartState.get_skills_design.set()
    else:
        user = await ContextHelper.get_user(state)
        user.desired_department = answer
        await update_user_by_telegram_id(message.from_user.id, user)
        await ContextHelper.add_user(user, state)
        await message.answer('Введите вашу ссылку на gitlab 🌐',
                             reply_markup=StopBotKeyboard.get_reply_keyboard())
        await StartState.get_skills_dev.set()


@logger.catch
@dp.message_handler(state=StartState.get_skills_design)
async def get_skills_design(message: types.Message, state: FSMContext):
    logger.info(f'StartState.get_skills_design с содержимым: {message.text} '
                f'-> @{message.from_user.username} (id: {message.from_user.id})')
    answer = message.text
    if await Validations.is_command(answer):
        await message.answer('Вы ввели команду. Пожалуйста, введите ссылку на ваш Behance',
                             reply_markup=ReplyKeyboardRemove())
    elif not validators.url(answer):
        await message.answer('Введите, пожалуйста, корректную ссылку на Behance',
                             reply_markup=ReplyKeyboardRemove())
    else:
        user = await ContextHelper.get_user(state)
        user.behance = answer
        await update_user_by_telegram_id(message.from_user.id, user)
        await ContextHelper.add_user(user, state)
        await message.answer('Введите, пожалуйста, из какого вы города',
                             reply_markup=StopBotKeyboard.get_reply_keyboard())
        await StartState.get_city.set()


@logger.catch
@dp.message_handler(state=StartState.get_skills_dev)
async def get_skills_dev(message: types.Message, state: FSMContext):
    logger.info(f'StartState.get_skills_dev с содержимым: {message.text} '
                f'-> @{message.from_user.username} (id: {message.from_user.id})')
    answer = message.text
    if await Validations.is_command(answer):
        await message.answer('Вы ввели команду. Пожалуйста, введите ссылку на ваш Gitlab',
                             reply_markup=StopBotKeyboard.get_reply_keyboard())
    elif not validators.url(answer):
        await message.answer('Введите, пожалуйста, корректную ссылку на Gitlab',
                             reply_markup=StopBotKeyboard.get_reply_keyboard())
    else:
        user = await ContextHelper.get_user(state)
        user.git = answer
        await update_user_by_telegram_id(message.from_user.id, user)
        await ContextHelper.add_user(user, state)
        await message.answer('Введите, пожалуйста, из какого вы города',
                             reply_markup=StopBotKeyboard.get_reply_keyboard())
        await StartState.get_city.set()


@logger.catch
@dp.message_handler(state=StartState.get_city)
async def get_city(message: types.Message, state: FSMContext):
    logger.info(f'StartState.get_city с содержимым: {message.text} '
                f'-> @{message.from_user.username} (id: {message.from_user.id})')
    answer = message.text
    if await Validations.is_command(answer):
        await message.answer('Вы ввели команду. Пожалуйста, введите город, в котором проживаете',
                             reply_markup=StopBotKeyboard.get_reply_keyboard())
    elif await Validations.length(answer, minimum=0, maximum=30):
        await message.answer('Нельзя использовать более 30 символов')
    else:
        user = await ContextHelper.get_user(state)
        user.city = answer
        await update_user_by_telegram_id(message.from_user.id, user)
        await ContextHelper.add_user(user, state)
        await message.answer('Напишите, пожалуйста, откуда Вы узнали о Школе IT?',
                             reply_markup=StopBotKeyboard.get_reply_keyboard())
        await StartState.get_source.set()


@logger.catch
@dp.message_handler(state=StartState.get_source)
async def get_source(message: types.Message, state: FSMContext):
    logger.info(f'StartState.get_source с содержимым: {message.text} '
                f'-> @{message.from_user.username} (id: {message.from_user.id})')
    answer = message.text
    if await Validations.is_command(answer):
        await message.answer('Вы ввели команду. Пожалуйста, введите откуда Вы узнали о школе',
                             reply_markup=StopBotKeyboard.get_reply_keyboard())
    elif await Validations.length(answer, minimum=0, maximum=30):
        await message.answer('Нельзя использовать более 30 символов')
    else:
        user = await ContextHelper.get_user(state)
        user.source_of_knowledge = answer
        await update_user_by_telegram_id(message.from_user.id, user)
        await ContextHelper.add_user(user, state)
        await message.answer('Введите ваши навыки\n'
                             'Например: Python, Postgresql, Git, FastAPI, '
                             'Django, Go, aiogramm, asyncio', reply_markup=StopBotKeyboard.get_reply_keyboard())
        await StartState.expectations.set()


@logger.catch
@dp.message_handler(state=StartState.expectations)
async def get_goals(message: types.Message, state: FSMContext):
    logger.info(f'StartState.expectations с содержимым: {message.text} '
                f'-> @{message.from_user.username} (id: {message.from_user.id})')
    answer = message.text
    if await Validations.is_command(answer):
        await message.answer('Вы ввели команду. Пожалуйста, введите ваши навыки',
                             reply_markup=StopBotKeyboard.get_reply_keyboard())
    else:
        user = await ContextHelper.get_user(state)
        user.skills = answer
        await update_user_by_telegram_id(message.from_user.id, user)
        await ContextHelper.add_user(user, state)
        await message.answer('Сколько времени (часов в неделю) Вы готовы уделять проекту?',
                             reply_markup=StopBotKeyboard.get_reply_keyboard())
        await StartState.time_for_work.set()


# 1111111111111111111111111111
@logger.catch
@dp.message_handler(state=StartState.time_for_work)
async def get_time_for_work(message: types.Message, state: FSMContext):
    logger.info(f'StartState.time_for_work с содержимым: {message.text} '
                f'-> @{message.from_user.username} (id: {message.from_user.id})')
    answer = message.text
    if await Validations.is_command(answer):
        await message.answer('Вы ввели команду. '
                             'Пожалуйста, введите сколько часов в неделю Вы готовы уделять проекту?',
                             reply_markup=StopBotKeyboard.get_reply_keyboard())
    else:
        user = await ContextHelper.get_user(state)
        user.time_for_work = answer
        await update_user_by_telegram_id(message.from_user.id, user)
        await ContextHelper.add_user(user, state)
        await message.answer('Какие курсы Вы закончили?',
                             reply_markup=StopBotKeyboard.get_reply_keyboard())
        await StartState.education.set()

# 22222222222222222222222
@logger.catch
@dp.message_handler(state=StartState.education)
async def get_education(message: types.Message, state: FSMContext):
    logger.info(f'StartState.education с содержимым: {message.text} '
                f'-> @{message.from_user.username} (id: {message.from_user.id})')
    answer = message.text
    if await Validations.is_command(answer):
        await message.answer('Вы ввели команду. Пожалуйста, введите какие курсы вы закончили?',
                             reply_markup=StopBotKeyboard.get_reply_keyboard())
    else:
        user = await ContextHelper.get_user(state)
        user.education = answer
        await update_user_by_telegram_id(message.from_user.id, user)
        await ContextHelper.add_user(user, state)
        await message.answer('Есть ли у Вас желание принимать участие в управлении школой?',
                             reply_markup=StopBotKeyboard.get_reply_keyboard())
        await StartState.management_wish.set()

# 333333333333333333333333333333333333
@logger.catch
@dp.message_handler(state=StartState.management_wish)
async def get_management_wish(message: types.Message, state: FSMContext):
    logger.info(f'StartState.management_wish с содержимым: {message.text} '
                f'-> @{message.from_user.username} (id: {message.from_user.id})')
    answer = message.text
    if await Validations.is_command(answer):
        await message.answer('Вы ввели команду. '
                             'Пожалуйста, введите есть ли у вас желание принимать участие в управлении школой.',
                             reply_markup=StopBotKeyboard.get_reply_keyboard())
    elif await Validations.length(answer, minimum=0, maximum=30):
        await message.answer('Нельзя использовать более 30 символов')
    else:
        user = await ContextHelper.get_user(state)
        user.management_wish = answer
        await update_user_by_telegram_id(message.from_user.id, user)
        await ContextHelper.add_user(user, state)

        # await message.answer('Напишите, пожалуйста, откуда Вы узнали о Школе IT?',
        #                      reply_markup=StopBotKeyboard.get_reply_keyboard())
        # await StartState.get_source.set()
        await message.answer('Ваша анкета отправлена на проверку. '
                             'Пока ее не проверят, функционал бота не доступен',
                             reply_markup=CheckAccessKeyboard.get_reply_keyboard(add_stop=False))
        await bot.send_message(chat_id=settings.TELEGRAM_MODERS_CHAT_ID, text=f'Пришла карточка {user.tg_login}')
        await send_full_card(chat_id=settings.TELEGRAM_MODERS_CHAT_ID,
                             user=user,
                             reply_markup=ModeratorSurveyInlineKeyboard(
                                 page=0,
                                 telegram_id=user.telegram_id,
                                 user_name=user.tg_login
                             ).get_inline_keyboard())
        await StartState.check_questionnaire.set()
# vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv




# @logger.catch
# @dp.message_handler(state=StartState.development_vector)
# async def get_development_vector(message: types.Message, state: FSMContext):
#     logger.info(f'StartState.development_vector с содержимым: {message.text} '
#                 f'-> @{message.from_user.username} (id: {message.from_user.id})')
#     answer = message.text
#     if await Validations.is_command(answer):
#         await message.answer('Вы ввели команду. Пожалуйста, введите ваши ожидания от школы',
#                              reply_markup=StopBotKeyboard.get_reply_keyboard(add_stop=False))
#     else:
#         user = await ContextHelper.get_user(state)
#         user.goals = f'Ожидания: {answer}'
#         await update_user_by_telegram_id(message.from_user.id, user)
#         await ContextHelper.add_user(user, state)
#         await message.answer('Введите желаемый вектор развития',
#                              reply_markup=ReplyKeyboardRemove())
#         await StartState.finish_questions.set()
#
#
# @logger.catch
# @dp.message_handler(state=StartState.finish_questions)
# async def finish_questions(message: types.Message, state: FSMContext):
#     logger.info(f'StartState.finish_questions с содержимым: {message.text} '
#                 f'-> @{message.from_user.username} (id: {message.from_user.id})')
#     answer = message.text
#     if await Validations.is_command(answer):
#         await message.answer('Вы ввели команду. Пожалуйста, введите желаемый вектор развития',
#                              reply_markup=StopBotKeyboard.get_reply_keyboard(add_stop=False))
#     else:
#         user = await ContextHelper.get_user(state)
#         user.goals += f'\nВектор развития: {answer}'
#         await update_user_by_telegram_id(message.from_user.id, user)
#         await ContextHelper.add_user(user, state)
#         await message.answer('Ваша анкета отправлена на проверку. '
#                              'Пока ее не проверят, функционал бота не доступен',
#                              reply_markup=CheckAccessKeyboard.get_reply_keyboard(add_stop=False))
#         await bot.send_message(chat_id=settings.TELEGRAM_MODERS_CHAT_ID, text=f'Пришла карточка {user.tg_login}')
#         await send_full_card(chat_id=settings.TELEGRAM_MODERS_CHAT_ID,
#                              user=user,
#                              reply_markup=ModeratorSurveyInlineKeyboard(
#                                  page=0,
#                                  telegram_id=user.telegram_id,
#                                  user_name=user.tg_login
#                              ).get_inline_keyboard())
#         await StartState.check_questionnaire.set()




# @logger.catch
# @dp.message_handler(state=StartState.check_questionnaire)
# async def check_questionnaire(message: types.Message, state: FSMContext):
#     logger.info(f'StartState.check_questionnaire с содержимым: {message.text} '
#                 f'-> @{message.from_user.username} (id: {message.from_user.id})')
#     answer = message.text
#     if answer == CheckAccessKeyboard.A_CHECK_ACCESS:
#         try:
#             user = await get_user_by_tg_login(f'@{message.from_user.username}')
#             if user.is_approved:
#                 text = 'Анкета одобрена, поздравляем!\n\nТебе необходимо вступить во все ' \
#                        'следующие группы в течение 2 дней:\n{}\n'. \
#                     format('Школа IT:\nhttps://t.me/+qGGF9z5Jy8MwMDA8'
#                            '\n\nПроекты:\nhttps://t.me/+HwhF6emf-asxYmMy')
#                 await message.answer(text,
#                                      reply_markup=JoinedKeyboard.get_reply_keyboard(add_stop=False))
#                 await StartState.send_teamleads.set()
#             else:
#                 await message.answer('Пока не одобрено',
#                                      reply_markup=CheckAccessKeyboard.get_reply_keyboard(add_stop=False))
#         # except AttributeError:   # если удалили анкету в бд его нет и нет is_approved
#         #     await bot.send_message(text='Что-то пошло не так, Вашу анкету удалили. '
#         #                                 'Попробуйте заполнить анкету заново или '
#         #                                 'обратитесь к тимлиду или модератору',
#         #                            chat_id=message.chat.id,
#         #                            reply_markup=ReplyKeyboardRemove())
#         #     await state.finish()
#         except AttributeError:
#             channels = settings.TELEGRAM_SCHOOL_CHATS
#             user_id = message.from_user.id
#             user_status = await bot.get_chat_member(chat_id=channels[0], user_id=user_id)
#
#             if user_status.status == 'kicked':
#                 await bot.send_message(text='Вы заблокированы в одном из наших чатов. '
#                                             'Обратитесь к тимлиду или модератору',
#                                        chat_id=message.chat.id,
#                                        reply_markup=ReplyKeyboardRemove())
#                 await StartState.cycle.set()
#             else:
#                 await bot.send_message(chat_id=message.chat.id,
#                                        text='Неверно заполнена анкета, заполните как в примере')
#                 moder = await get_random_moder()
#                 await send_card(message.chat.id, moder)
#                 await bot.send_message(chat_id=message.chat.id,
#                                        text='Для перезаполнения анкеты нажмите на кнопку ниже',
#                                        reply_markup=MoveToRefilling.get_reply_keyboard(add_stop=False))
#                 await StartState.rules_for_refilling.set()
#     else:
#         await message.answer('Чтобы проверить анкету нажмите на кнопку ниже',
#                              reply_markup=CheckAccessKeyboard.get_reply_keyboard(add_stop=False))
#         await StartState.check_questionnaire.set()
@logger.catch
@dp.message_handler(state=StartState.check_questionnaire)
async def check_questionnaire(message: types.Message, state: FSMContext):
    logger.info(f'StartState.check_questionnaire с содержимым: {message.text} '
                f'-> @{message.from_user.username} (id: {message.from_user.id})')
    answer = message.text
    if answer == CheckAccessKeyboard.A_CHECK_ACCESS:
        user = await get_user_by_tg_login(f'@{message.from_user.username}')
        if user:
            if user.is_approved:
                text = 'Анкета одобрена, поздравляем!\n\nТебе необходимо вступить во все ' \
                       'следующие группы в течение 2 дней:\n{}\n'. \
                    format('Школа IT:\nhttps://t.me/+qGGF9z5Jy8MwMDA8'
                           '\n\nПроекты:\nhttps://t.me/+HwhF6emf-asxYmMy')
                await message.answer(text,
                                     reply_markup=JoinedKeyboard.get_reply_keyboard(add_stop=False))
                await StartState.send_teamleads.set()
            else:
                await message.answer('Пока не одобрено',
                                     reply_markup=CheckAccessKeyboard.get_reply_keyboard(add_stop=False))

        else:
            channels = settings.TELEGRAM_SCHOOL_CHATS
            user_id = message.from_user.id
            user_status = await bot.get_chat_member(chat_id=channels[0], user_id=user_id)

            if user_status.status == 'kicked':
                await bot.send_message(text='Вы заблокированы в одном из наших чатов. '
                                            'Обратитесь к тимлиду или модератору',
                                       chat_id=message.chat.id,
                                       reply_markup=ReplyKeyboardRemove())
                await StartState.cycle.set()
            else:
                await bot.send_message(chat_id=message.chat.id,
                                       text='Неверно заполнена анкета, заполните как в примере')
                moder = await get_random_moder()
                await send_card(message.chat.id, moder)
                await bot.send_message(chat_id=message.chat.id,
                                       text='Для перезаполнения анкеты нажмите на кнопку ниже',
                                       reply_markup=MoveToRefilling.get_reply_keyboard(add_stop=False))
                await StartState.rules_for_refilling.set()
    else:
        await message.answer('Чтобы проверить анкету нажмите на кнопку ниже',
                             reply_markup=CheckAccessKeyboard.get_reply_keyboard(add_stop=False))
        await StartState.check_questionnaire.set()


@logger.catch
@dp.message_handler(state=StartState.send_teamleads)
async def send_teamleads(message: types.Message):
    logger.info(f'StartState.send_teamleads с содержимым: {message.text} '
                f'-> @{message.from_user.username} (id: {message.from_user.id})')
    text = 'Привет! \n' \
           'Новеньким и не совсем новеньким лучше написать тимлидам направлений/проектов,' \
           ' вас любезно добавят в чат и постараются ответить на ваши вопросы\n\n' \
           'Лиды направлений:\n' \
           '@Glebser9 - Глеб @yuuumei - Фаррух - лидеры Backend\n' \
           '@Ivanchurakof - Иван - лидер Frontend\n' \
           '@Sor_ig - Игорь - лидер DS/ML\n' \
           '@abstraducks - Лиза - лидер Дизайна\n' \
           '@poddubniysergey198 - Сергей - лидер Android/ IOS разработки\n' \
           '@poddubniysergey198 - Сергей - лидер отдела Адаптации\n' \
           '@MicoDi - Мила - лидер отдела тестирования и безопасности\n' \
           '@aanatyrnal - Ангелина по общим вопросам\n' \
           '@MicoDi - Мила - руководитель школы IT' 
    await message.answer(text,
                         reply_markup=IHaveRead.get_reply_keyboard(add_stop=False))
    await StartState.send_instructions.set()


@logger.catch
@dp.message_handler(state=StartState.send_instructions)
async def check_membership(message: types.Message):
    logger.info(f'StartState.send_instructions с содержимым: {message.text} '
                f'-> @{message.from_user.username} (id: {message.from_user.id})')

    text = 'Привет!\n\n' \
           'И вот прекрасный бот дал тебе ссылки на пустой чат Школы и на канал с Проектами.' \
           ' Ты посмотрел(а) и не знаешь, что делать? Сейчас расскажу:\n\n' \
           '1. Напиши своему тимлиду. Тимлид – звезда, которая поведет тебя. В зависимости от направления, тимлид:\n' \
           '-  может дать тестовое задание в целом (для оценки твоих хардов) или подскажет' \
           ' по заданию для каждого из проекта;\n' \
           '- даст ссылку на чат направления (сразу или после прохождения тестового задания);\n' \
           '- ответит на другие вопросы;\n' \
           '- подскажет, в какие проекты открыт набор.\n\n' \
           '2. Если у тебя есть желание дополнительно прокачаться и принять активное участие в помощи' \
           ' и развитии школы (отдел контроля и адаптации помогут тебе).\n' \
           'Отдел контроля поможет освоить направление project-manager (писать Карену), а отдел адаптации' \
           ' оказывает помощь новым участникам (если хочешь стать куратором, пиши лидеру отдела адаптации).\n\n' \
           'У нас также есть крутой отдел общения с фондами. А как по-другому у нас появляются проекты,' \
           ' а у участников Школы классные тасочки и крутой практический опыт? Также прекрасные люди,' \
           ' которые общаются с обучающими/учебными платформами (поэтому количество участников растет).\n\n' \
           'В Школе запущено онлайн-обучение по нескольким направлениям. ' \
           'Для онлайн-обучения - специальный чат и анонс в общем чате. \n\n' \
           'Участники Школы разрабатывают собственный сайт:\n' \
           'http://guild-of-developers.ru\n\n' \
           'Шикарные функции для развития:\n' \
           '1. Предложить проект для реализации;\n' \
           '2. Стать тимлидом проекта по своему направлению;\n' \
           '3. Стать проджект-менеджером проекта\n\n' \
           'Пятничные встречи в 19:00\n' \
           'Если вы из Москвы, я бы посоветовал посетить. Для онлайна подключение в чате Уроков.\n\n'
    await message.answer(text, reply_markup=IHaveRead.get_reply_keyboard(add_stop=False))
    await StartState.adaptaion_chat.set()


@logger.catch
@dp.message_handler(state=StartState.adaptaion_chat)
async def adaptaion_chat(message: types.Message):
    text = 'В чате адаптации тебе объяснят про устройство школы и ответят на оставшиеся вопросы, вступай!\n' \
           'https://t.me/+fm_N4tk4oMRhMmY6'
    await message.answer(text, reply_markup=JoinedKeyboard.get_reply_keyboard(add_stop=False))
    await StartState.friday_meetings.set()


@logger.catch
@dp.message_handler(state=StartState.friday_meetings)
async def friday_meetings(message: types.Message):
    text = '❗️ВНИМАНИЕ❗️\n\n' \
           'Трансляции пятничных собраний переезжают в чат - Школа  IT | Уроки:\n' \
           'https://t.me/+YgsWJg_2274xYmI0'
    await message.answer(text, reply_markup=JoinedAllKeyboard.get_reply_keyboard(add_stop=False))
    await StartState.check_membership.set()


@logger.catch
@dp.message_handler(state=StartState.check_membership)
async def check_membership(message: types.Message, state: FSMContext):
    logger.info(f'StartState.check_membership с содержимым: {message.text} '
                f'-> @{message.from_user.username} (id: {message.from_user.id})')
    is_member = True
    channels = settings.TELEGRAM_SCHOOL_CHATS
    is_first_check = True
    user_id = message.from_user.id

    while True:
        for channel in channels:
            user_status = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if user_status.status == 'kicked':
                await message.answer('Вы заблокированы в одном из наших чатов. '
                                     'Обратитесь к тимлиду или модератору',
                                     reply_markup=ReplyKeyboardRemove())
                await delete_user(user_id, channels)
                await state.finish()
                return
            elif user_status.status == 'left':
                is_member = False
                if is_first_check:
                    await message.answer('Если Вы не вступите '
                                         'в течение следующих суток, Ваша анкета будет удалена',
                                         reply_markup=ReplyKeyboardRemove())
                    is_first_check = False
                    await asyncio.sleep(86_400)
                    break
                else:
                    await bot.send_message(chat_id=settings.TELEGRAM_MODERS_CHAT_ID,
                                           text=f'Пользователь @{message.from_user.username} кикнут'
                                                f' по истечению двух суток')
                    await message.answer('Жаль, но придется нам расстаться. До свидания',
                                         reply_markup=ReplyKeyboardRemove())
                    await delete_user(user_id, channels)
                    await StartState.cycle.set()
                    return
        if is_member:
            await message.answer('Спасибо, что Вы с нами!', reply_markup=ReplyKeyboardRemove())
            await state.finish()
            return


@logger.catch
@dp.message_handler(state=StartState.get_moder)
async def get_moder(message: types.Message, state: FSMContext):
    logger.info(f'StartState.get_moder с содержимым: {message.text} '
                f'-> @{message.from_user.username} (id: {message.from_user.id})')
    answer = message.text
    if answer == settings.SECRET_KEY:
        await update_user_status(message.from_user.id)
        await message.answer('Ваша анкета одобрена и права модератора получены',
                             reply_markup=ReplyKeyboardRemove())
        await state.finish()
    else:
        await message.answer('Неверный ключ доступа',
                             reply_markup=StopBotKeyboard.get_reply_keyboard())
        await StartState.check_questionnaire.set()


@logger.catch
@dp.message_handler(state=StartState.cycle)
async def cycle():
    await StartState.cycle.set()
