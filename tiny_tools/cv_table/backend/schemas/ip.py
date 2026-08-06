"""IP Schema。"""

from datetime import datetime
from pydantic import BaseModel, Field


class IPCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    sys_id: int
    description: str = ""


class IPUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    sys_id: int | None = None
    description: str | None = None


class IPResponse(BaseModel):
    id: int
    name: str
    sys_id: int
    sys_name: str = ""
    description: str
    created_at: datetime
    case_count: int = 0

    class Config:
        from_attributes = True
