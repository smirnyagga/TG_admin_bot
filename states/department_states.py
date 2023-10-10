from aiogram.dispatcher.filters.state import StatesGroup, State


class DepartmentStates(StatesGroup):
    moderator_choice = State()
    new_department = State()
    delete_department = State()
    change_department_name_get_name = State()
    change_department_name = State()
    change_team_lead_name_get_name = State()
    change_team_lead_name = State()
