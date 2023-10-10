from aiogram.dispatcher.filters.state import StatesGroup, State


class ProjectStates(StatesGroup):
    moderator_choice = State()
    new_project = State()
    delete_project = State()
    change_project_name_get_name = State()
    change_project_name = State()
    change_team_lead_name_get_name = State()
    change_team_lead_name = State()
