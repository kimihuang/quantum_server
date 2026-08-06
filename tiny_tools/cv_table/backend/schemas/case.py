"""Case Schema — 简化版，直接归属 IP。"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class CaseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    ip_id: int
    description: str = ""
    priority: str = Field(default="P2", pattern=r"^P[0-2]$")
    status: str = Field(default="not_run", pattern=r"^(not_run|pass|fail|blocked|skip)$")
    owner: str = ""
    custom_fields: Optional[dict] = None


class CaseUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    ip_id: int | None = None
    description: str | None = None
    priority: str | None = Field(None, pattern=r"^P[0-2]$")
    status: str | None = Field(None, pattern=r"^(not_run|pass|fail|blocked|skip)$")
    owner: str | None = None
    custom_fields: Optional[dict] = None


class CaseFilter(BaseModel):
    sys_id: int | None = None
    ip_id: int | None = None
    status: str | None = None
    priority: str | None = None
    keyword: str | None = None
    page: int = 1
    page_size: int = 20


class CaseResponse(BaseModel):
    id: int
    name: str
    ip_id: int
    ip_name: str = ""
    sys_id: int = 0
    sys_name: str = ""
    description: str
    priority: str
    status: str
    owner: str
    custom_fields: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CaseExecutionResponse(BaseModel):
    id: int
    case_id: int
    status: str
    log: str
    executor: str
    executed_at: datetime

    class Config:
        from_attributes = True


class CaseStatusUpdate(BaseModel):
    status: str = Field(pattern=r"^(pass|fail|blocked|skip)$")
    executor: str = ""
    log: str = ""


class CaseBatchUpdate(BaseModel):
    ids: list[int]
    status: str | None = Field(None, pattern=r"^(not_run|pass|fail|blocked|skip)$")
    priority: str | None = Field(None, pattern=r"^P[0-2]$")
    owner: str | None = None


class CaseStats(BaseModel):
    total: int
    pass_count: int
    fail_count: int
    not_run_count: int
    blocked_count: int
    skip_count: int
    pass_rate: float


class GroupStats(BaseModel):
    group_id: int
    group_name: str
    total: int
    pass_count: int
    fail_count: int
    blocked_count: int
    pass_rate: float
