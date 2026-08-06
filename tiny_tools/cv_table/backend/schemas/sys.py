"""Sys Schema。"""

from datetime import datetime
from pydantic import BaseModel, Field


class SysCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = ""


class SysUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None


class SysResponse(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime
    ip_count: int = 0
    case_count: int = 0

    class Config:
        from_attributes = True
