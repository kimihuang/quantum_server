"""Scenario Schema。"""

from datetime import datetime
from pydantic import BaseModel, Field


class ScenarioCreate(BaseModel):
    """创建场景请求。"""
    name: str = Field(min_length=1, max_length=100)
    description: str = ""


class ScenarioUpdate(BaseModel):
    """更新场景请求。"""
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None


class ScenarioResponse(BaseModel):
    """场景响应。"""
    id: int
    name: str
    description: str
    created_at: datetime

    class Config:
        from_attributes = True
