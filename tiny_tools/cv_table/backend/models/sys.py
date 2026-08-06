"""SYS 模型 — 芯片系统（CPU_SYS, DDR_SYS 等）。"""

from datetime import datetime
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Sys(Base):
    __tablename__ = "systems"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, comment="SYS名称")
    description: Mapped[str] = mapped_column(String(500), default="", comment="描述")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="创建时间"
    )

    # 关系
    ips: Mapped[list["IP"]] = relationship("IP", back_populates="sys", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Sys(id={self.id}, name={self.name})>"
