"""CustomColumn Schema。"""

from datetime import datetime
from pydantic import BaseModel, Field


class CustomColumnCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    field_key: str = Field(min_length=1, max_length=50, pattern=r"^[a-zA-Z][a-zA-Z0-9_]*$")
    column_type: str = Field(default="text", pattern=r"^(text|number|select)$")
    options: str | None = None
    is_required: bool = False


class CustomColumnUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    column_type: str | None = Field(None, pattern=r"^(text|number|select)$")
    options: str | None = None
    is_required: bool | None = None
    sort_order: int | None = None


class CustomColumnResponse(BaseModel):
    id: int
    name: str
    field_key: str
    column_type: str
    options: str | None
    is_required: bool
    sort_order: int
    created_at: datetime

    class Config:
        from_attributes = True
