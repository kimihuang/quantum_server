"""IP 模块 — 芯片 IP 模块，归属于某个 SYS。"""

from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class IP(Base):
    __tablename__ = "ips_v2"
    __table_args__ = (
        UniqueConstraint("name", "sys_id", name="uq_ip_name_sys"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="IP名称")
    sys_id: Mapped[int] = mapped_column(ForeignKey("systems.id"), nullable=False, comment="所属SYS")
    description: Mapped[str] = mapped_column(String(500), default="", comment="描述")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="创建时间"
    )

    # 关系
    sys: Mapped["Sys"] = relationship("Sys", back_populates="ips")

    def __repr__(self) -> str:
        return f"<IP(id={self.id}, name={self.name}, sys_id={self.sys_id})>"
