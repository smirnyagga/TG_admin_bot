import datetime
from typing import Optional

from pydantic import BaseModel


# class User(BaseModel):
#     user_id: int = -1
#     telegram_id: int = -1
#     surname: Optional[str] = ''
#     name: str = ''
#     patronymic: Optional[str] = ''
#     gender: str = ''
#     photo: Optional[bytes] = bytearray([])
#     email: str = ''
#     git: str = ''
#     behance: Optional[str] = ''
#     tg_login: str = ''
#     desired_department: str = 'EmptyDepartment'
#     skills: str = ''
#     goals: str = ''
#     city: str = ''
#     source_of_knowledge: str = ''
#     lead_description: str = ''
#     join_time: datetime.date = datetime.date.today()
#     is_moderator: bool = False
#     is_approved: bool = False
#
#     class Config:
#         arbitrary_types_allowed = True

class User(BaseModel):
    user_id: int = -1
    telegram_id: int = -1
    surname: Optional[str] = ''
    name: str = ''
    patronymic: Optional[str] = ''
    gender: str = ''
    photo: Optional[bytes] = bytearray([])
    email: str = ''
    git: str = ''
    behance: Optional[str] = ''
    tg_login: str = ''
    desired_department: str = 'EmptyDepartment'
    time_for_work: str = ''  #!!!!!!!!!new
    skills: str = ''
    education: str = ''   #!!!!!!!!!new
    management_wish: str = ''  #!!!!!!!!!new
    # goals: str = ''
    city: str = ''
    source_of_knowledge: str = ''
    lead_description: str = ''
    join_time: datetime.date = datetime.date.today()
    is_moderator: bool = False
    is_approved: bool = False

    class Config:
        arbitrary_types_allowed = True
