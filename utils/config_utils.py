import pathlib

from loguru import logger


class ConfigUtils:
    @staticmethod
    @logger.catch
    def get_project_root():
        logger.info('Получение пути корня проекта')
        return pathlib.Path(__file__).parent.parent

    @staticmethod
    @logger.catch
    def get_temp_path():
        logger.info('Получение пути директории temp')
        return str(pathlib.PurePath(ConfigUtils.get_project_root(), 'temp'))
