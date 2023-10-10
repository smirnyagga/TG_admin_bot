from typing import Optional

from pydantic import BaseModel


class Department(BaseModel):
    department_id: int = 0
    department: str = ''
    team_lead: Optional[str] = ''
