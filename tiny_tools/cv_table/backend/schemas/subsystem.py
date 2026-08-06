"""Subsystem Schema。"""

from datetime import datetime
from pydantic import BaseModel, Field


class SubsystemCreate(BaseModel):
    """创建子系统请求。"""
    name: str = Field(min_length=1, max_length=100)
    ip_id: int
    description: str = ""


class SubsystemUpdate(BaseModel):
    """更新子系统请求。"""
    name: str | None = Field(None, min_length=1, max_length=100)
    ip_id: int | None = None
    description: str | None = None


class SubsystemResponse(BaseModel):
    """子系统响应。"""
    id: int
    name: str
    ip_id: int
    ip_name: str = ""
    description: str
    created_at: datetime

    class Config:
        from_attributes = True
