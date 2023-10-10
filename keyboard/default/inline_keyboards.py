from keyboard.default.button_factory import ButtonFactory
from pkg.db.models.user import User


class ModeratorSurveyInlineKeyboard(ButtonFactory):

    def __init__(self, page, telegram_id, user_name, ):
        self.APPROVE = {
            'Одобрить': f'approve#{page}#{telegram_id}#{user_name}'}
        self.REFILLING = {
            'Перезаполнение': f'refilling#{page}#{telegram_id}#{user_name}'}
        self.DELETE = {
            'Удалить': f'delete_user#{page}#{telegram_id}#{user_name}'}


class ModeratorChangeDecisionInlineKeyboard(ButtonFactory):
    def __init__(self, telegram_id, field_name, field_value, ):
        self.APPROVE = {
            'Одобрить': f'approve_changes#{telegram_id}#{field_name}#{field_value}'}
        self.DECLINE = {
            'Отклонить': f'decline_changes#{telegram_id}#{field_name}#{field_value}'}


class BackInlineKeyboard(ButtonFactory):

    def __init__(self):
        self.BACK = {
            'Вернуться на главную': 'back'
        }


class UserChangeCardInlineKeyboard(ButtonFactory):

    def __init__(self, page, user: User, callback_data: str, back_button=False, ):
        self.SURNAME = {
            'Фамилия': f'{callback_data}#{page}#surname#{user.telegram_id}'}
        self.NAME = {
            'Имя': f'{callback_data}#{page}#name#{user.telegram_id}'}
        self.PATRONYMIC = {
            'Отчество': f'{callback_data}#{page}#patronymic#{user.telegram_id}'}
        self.GENDER = {
            'Пол': f'{callback_data}#{page}#gender#{user.telegram_id}'}
        self.SKILLS = {
            'Скилы': f'{callback_data}#{page}#skills#{user.telegram_id}'}
        self.EMAIL = {
            'Почта': f'{callback_data}#{page}#email#{user.telegram_id}'}
        self.CITY = {
            'Город': f'{callback_data}#{page}#city#{user.telegram_id}'}
        self.TG_LOGIN = {
            'Логин в Telegram': f'{callback_data}#{page}#tg_login#{user.telegram_id}'}
        self.DESIRED_DEPARTMENT = {
            'Отдел': f'{callback_data}#{page}#desired_department#{user.telegram_id}'}
        self.SOURCE_OF_KNOWLEDGE = {
            'Откуда узнал о школе': f'{callback_data}#{page}#source_of_knowledge#{user.telegram_id}'}
        self.TIME = {
            'Время для работы над проектом': f'{callback_data}#{page}#time_for_work#{user.telegram_id}'}
        self.GOALS = {
            'Курсы': f'{callback_data}#{page}#education#{user.telegram_id}'}
        self.GOALS = {
            'Участие в управлении': f'{callback_data}#{page}#management_wish#{user.telegram_id}'}
        self.PHOTO = {
            'Фото': f'{callback_data}#{page}#photo#{user.telegram_id}'}
        if back_button:
            self.BACK = BackInlineKeyboard().BACK


class ModeratorChangeCardInlineKeyboard(UserChangeCardInlineKeyboard):

    def __init__(self, page, user: User, callback_data: str):
        super().__init__(page, user, callback_data)
        self.LEAD_DESCRIPTION = {
            'Описание тимлида': f'{callback_data}#{page}#lead_description#{user.telegram_id}'}
        if user.git != '':
            self.GIT = {
                'Гит': f'{callback_data}#{page}#git#{user.telegram_id}'}
        elif user.behance != '':
            self.BEHANCE = {
                'Гит': f'{callback_data}#{page}#behance#{user.telegram_id}'}
