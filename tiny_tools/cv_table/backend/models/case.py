"""Case 模型 — 验证用例，直接归属某个 IP。"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Case(Base):
    __tablename__ = "cases_v2"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, comment="Case名称")
    ip_id: Mapped[int] = mapped_column(ForeignKey("ips_v2.id"), nullable=False, comment="所属IP")
    description: Mapped[str] = mapped_column(Text, default="", comment="详细描述")
    priority: Mapped[str] = mapped_column(String(10), default="P2", comment="优先级: P0/P1/P2")
    status: Mapped[str] = mapped_column(String(20), default="not_run", comment="状态: not_run/pass/fail/blocked/skip")
    owner: Mapped[str] = mapped_column(String(50), default="", comment="负责人")
    custom_fields: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, comment="自定义字段")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )

    # 关系
    ip: Mapped["IP"] = relationship("IP")
    executions: Mapped[list["CaseExecution"]] = relationship(
        "CaseExecution", back_populates="case", cascade="all, delete-orphan",
        order_by="CaseExecution.executed_at.desc()"
    )

    def __repr__(self) -> str:
        return f"<Case(id={self.id}, name={self.name}, status={self.status})>"
