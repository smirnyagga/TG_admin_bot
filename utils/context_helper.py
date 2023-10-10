from aiogram.dispatcher import FSMContext
from loguru import logger

from pkg.db.models.user import User


class ContextHelper:
    @staticmethod
    @logger.catch
    async def get_user(context: FSMContext) -> User:
        logger.info('Получение юзера из ContextHelper')
        return await ContextHelper._get_context_by_name('user', context)

    @staticmethod
    @logger.catch
    async def add_user(user, context: FSMContext):
        logger.info('Добавление юзера в ContextHelper')
        await ContextHelper._set_context(user, 'user', context)

    @staticmethod
    @logger.catch
    async def add_some_data(data, context: FSMContext):
        logger.info(f'Добавление каких-либо данных в ContextHelper ({data})')
        await ContextHelper._set_context(data, 'data', context)

    @staticmethod
    @logger.catch
    async def get_some_data(context: FSMContext):
        logger.info('Получение каких-либо данных из ContextHelper')
        return await ContextHelper._get_context_by_some_data('data', context)

    @staticmethod
    @logger.catch
    async def get_tg_id(context: FSMContext) -> User:
        logger.info('Получение tg_id из ContextHelper')
        return await ContextHelper._get_context_by_tg_id('telegram_id', context)

    @staticmethod
    @logger.catch
    async def add_tg_id(telegram_id, context: FSMContext):
        logger.info('Добавление tg_id в ContextHelper')
        await ContextHelper._set_context(telegram_id, 'telegram_id', context)

    @staticmethod
    @logger.catch
    async def _set_context(data: ..., key: str, context: FSMContext) -> None:
        logger.info('Установка контекста в ContextHelper')
        async with context.proxy() as context:
            context[key] = data

    @staticmethod
    @logger.catch
    async def _get_context_by_name(name: str, context: FSMContext) -> ...:
        logger.info('Получение контекста из имени в ContextHelper')
        context = await context.get_data(name)
        if context is not None:
            return context.get(name)
        raise ValueError(f'Data for key: [{name}] is not found.')

    @staticmethod
    @logger.catch
    async def _get_context_by_tg_id(tg_id: str, context: FSMContext) -> ...:
        logger.info('Получение контекста из tg_id в ContextHelper')
        context = await context.get_data(tg_id)
        if context is not None:
            return context.get(tg_id)
        raise ValueError(f'Data for key: [{tg_id}] is not found.')

    @staticmethod
    @logger.catch
    async def _get_context_by_some_data(data, context: FSMContext) -> ...:
        logger.info('Получение контекста из каких-либо данных в ContextHelper')
        context = await context.get_data(data)
        if context is not None:
            return context.get(data)
        raise ValueError(f'Data for key: [{data}] is not found.')
