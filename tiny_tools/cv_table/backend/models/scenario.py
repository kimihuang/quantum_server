"""Scenario 模型 — 测试场景。"""

from datetime import datetime
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Scenario(Base):
    __tablename__ = "scenarios"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, comment="场景名称")
    description: Mapped[str] = mapped_column(String(500), default="", comment="描述")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="创建时间"
    )

    def __repr__(self) -> str:
        return f"<Scenario(id={self.id}, name={self.name})>"
