"""通用 Schema: 分页、错误响应、配置项。"""

from typing import TypeVar, Generic, Optional, Any
from pydantic import BaseModel

T = TypeVar("T")


class PaginationParams(BaseModel):
    """分页请求参数。"""
    page: int = 1
    page_size: int = 20


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应。"""
    items: list[T]
    total: int
    page: int
    page_size: int
    pages: int


class ErrorResponse(BaseModel):
    """统一错误响应。"""
    error: dict


class ConfigItem(BaseModel):
    """配置项（状态、优先级等）。"""
    value: str
    label: str
    color: str


class StatusTransition(BaseModel):
    """状态转换信息。"""
    current: str
    allowed: list[str]
