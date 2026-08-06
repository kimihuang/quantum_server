"""Subsystem 模型 — 芯片子系统。"""

from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Subsystem(Base):
    __tablename__ = "subsystems"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="子系统名称")
    ip_id: Mapped[int] = mapped_column(ForeignKey("ips.id"), nullable=False, comment="所属IP")
    description: Mapped[str] = mapped_column(String(500), default="", comment="描述")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="创建时间"
    )

    # 关系
    ip: Mapped["IP"] = relationship("IP", back_populates="subsystems")

    def __repr__(self) -> str:
        return f"<Subsystem(id={self.id}, name={self.name}, ip_id={self.ip_id})>"
