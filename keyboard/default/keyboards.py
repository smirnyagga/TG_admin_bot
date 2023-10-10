from aiogram.types import ReplyKeyboardMarkup

from pkg.db.department_func import get_all_departments
from pkg.db.project_func import get_all_projects
from .button_factory import ButtonFactory


class DepartmentsKeyboard(ButtonFactory):

    @classmethod
    async def __get_department(cls) -> None:
        all_departments = await get_all_departments()
        for department in all_departments:
            setattr(cls, department.department.upper(), department.department)

    @classmethod
    async def get_reply_keyboard(cls, one_time=False, **kwargs) -> ReplyKeyboardMarkup:
        await cls.__get_department()
        return super().get_reply_keyboard(one_time=one_time)

    @classmethod
    async def delete_department_button(cls, department):
        delattr(cls, department.upper())


class ProjectKeyboard(ButtonFactory):

    @classmethod
    async def __get_project(cls) -> None:
        all_projects = await get_all_projects()
        for project in all_projects:
            setattr(cls, project.project_name.upper(), project.project_name)

    @classmethod
    async def get_reply_keyboard(cls, one_time=False, **kwargs) -> ReplyKeyboardMarkup:
        await cls.__get_project()
        return super().get_reply_keyboard(one_time=one_time)

    @classmethod
    async def delete_project_button(cls, project):
        delattr(cls, project.upper())


class StopBotKeyboard(ButtonFactory):
    pass


class ChoiceKeyboard(ButtonFactory):
    A_READ_RULES = 'Ознакомиться с правилами 🤓'
    B_DONT_READ_RULES = 'Я не буду читать правила 😐'


class AgreementKeyboard(ButtonFactory):
    A_AGREE_WITH_RULES = 'Я согласен с правилами 😎'
    B_DONT_AGREE_WITH_RULES = 'Я не согласен с правилами 🤔'


class ConfidentialKeyboard(ButtonFactory):
    A_CONFIDENTIAL_AGREE = 'Я согласен на обработку персональных данных ✅'
    B_CONFIDENTIAL_DISAGREE = 'Я не согласен на обработку персональных данных ❌'


class CheckAccessKeyboard(ButtonFactory):
    A_CHECK_ACCESS = 'Проверить состояние анкеты ✅'


class DepartmentCommandsKeyboard(ButtonFactory):
    A_CREATE_DEPARTMENT = 'Создать новый отдел'
    B_DELETE_DEPARTMENT = 'Удалить отдел'
    C_CHANGE_DEPARTMENT_NAME = 'Сменить имя отдела'
    D_CHANGE_DEPARTMENT_LEAD = 'Сменить/добавить тим лида отдела'


class GenderKeyboard(ButtonFactory):
    A_MALE_GENDER = 'Мужской 👨'
    B_FEMALE_GENDER = 'Женский 👩‍🦰'


class PhotoKeyboard(ButtonFactory):
    A_WANT_UPLOAD_PHOTO = 'Да! Хочу загрузить свою фоточку 😎'
    B_DONT_WANT_UPLOAD_PHOTO = 'Нет, не буду загружать свое фото 🙂'


class ProjectCommandsKeyboard(ButtonFactory):
    A_CREATE_PROJECT = 'Создать новый проект'
    B_DELETE_PROJECT = 'Удалить проект'
    C_CHANGE_PROJECT_NAME = 'Сменить имя проекта'
    D_CHANGE_PROJECT_LEAD = 'Сменить/добавить тим лида проекта'


class ShowUserKeyboard(ButtonFactory):
    A_VIEW_ALL = 'Все'
    B_VIEW_ID = 'По ID в DB'
    C_VIEW_TG_LOGIN = 'По логину в TG'


class YesNoKeyboard(ButtonFactory):
    A_YES = 'Да ✅'
    B_NO = 'Нет ❌'


class JoinedKeyboard(ButtonFactory):
    A_USER_JOINED = 'Я вступил!'


class JoinedAllKeyboard(ButtonFactory):
    A_USER_JOINED_ALL = 'Я вступил во все чаты!'


class MoveToRefilling(ButtonFactory):
    A_MOVE_TO = 'Перезаполнить анкету'


class IHaveRead(ButtonFactory):
    A_I_HAVE_READ = 'Я ознакомился'
