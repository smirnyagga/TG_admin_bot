import validators
from aiogram import types
from loguru import logger

from keyboard.default.keyboards import StopBotKeyboard
from pkg.db.user_func import get_user_by_tg_id


class Validations:

    def __init__(self, field_name: str, message: types.Message):
        self.field_name = field_name
        self.message = message

    @logger.catch
    async def validate_tg_login_email_git(self) -> bool:
        logger.info('Валидация на tg_login, почты или Git')
        if self.field_name == 'tg_login':
            if self.message.text.startswith('@'):
                return True
            else:
                await self.message.answer(
                    'Пожалуйста, введите ваш логин с @\n(Например: @login)',
                    reply_markup=StopBotKeyboard.get_reply_keyboard())
                return False
        elif self.field_name == 'email':
            if validators.email(self.message.text):
                return True
            else:
                await self.message.answer('Вы ввели неверный формат почты',
                                          reply_markup=StopBotKeyboard.get_reply_keyboard())
                return False
        elif self.field_name == 'git' or self.field_name == 'behance':
            if validators.url(self.message.text):
                return True
            else:
                await self.message.answer(
                    'Введите, пожалуйста, корректную ссылку',
                    reply_markup=StopBotKeyboard.get_reply_keyboard())
                return False
        else:
            return True

    @staticmethod
    @logger.catch
    async def is_command(text: str) -> bool:
        logger.info('Валидация на команду tg')
        if text.startswith('/'):
            return True
        return False

    # @staticmethod
    # @logger.catch
    # async def moder_validation_for_supergroups(message: types.Message) -> bool:
    #     # logger.info('Валидация на тип чата')
    #     logger.info('Валидация на модератора')
    #     # if message.chat.type == types.ChatType.SUPERGROUP:
    #     #     print('это супергруппа')
    #     try:
    #         user = await get_user_by_tg_id(message.from_user.id)
    #         if user.is_moderator:
    #             return True
    #         return False
    #     except Exception as e:
    #         print(e)
    #         return False
    #     # else:
    #     #     return True

    # Валидация на тип чата. Чтобы бот отвечал только в личном чате. Или в группе, но только администраторам.

    @staticmethod
    @logger.catch
    async def moder_validation_for_supergroups(message: types.Message) -> bool:
        logger.info('Валидация на тип чата')
        if message.chat.type == types.ChatType.SUPERGROUP:
            # try:
            #     user = await get_user_by_tg_id(message.from_user.id)
            #     if user.is_moderator:
            #         return True
            #     print('пользователь не админ')
            #     return False
            # except Exception as e:
            #     print(e)
            #     return False
            return False
        # else:
        #     return True
        return True

    # Валидация на модератора. Чтобы доступ к данным был только у модераторов.

    @staticmethod
    @logger.catch
    async def validation_for_moderator(message: types.Message) -> bool:
        logger.info('Валидация на модератора')
        try:
            user = await get_user_by_tg_id(message.from_user.id)
            if user.is_moderator:
                return True
            return False
        except Exception as e:
            print(e)
            return False


    @staticmethod
    async def length(text: str, minimum: int, maximum: int) -> bool:
        logger.info('Валидация на длину сообщения')
        if minimum <= len(text) <= maximum:
            return False
        return True
