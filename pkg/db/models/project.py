from typing import Optional

from pydantic import BaseModel


class Project(BaseModel):
    project_id: int = 0
    project_name: str = ''
    team_lead: Optional[str] = ''
