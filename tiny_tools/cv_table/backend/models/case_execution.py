"""CaseExecution 模型 — 用例执行历史。"""

from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class CaseExecution(Base):
    __tablename__ = "case_executions_v2"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases_v2.id"), nullable=False, comment="所属Case")
    status: Mapped[str] = mapped_column(String(20), nullable=False, comment="执行结果")
    log: Mapped[str] = mapped_column(Text, default="", comment="执行日志")
    executor: Mapped[str] = mapped_column(String(50), default="", comment="执行人")
    executed_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="执行时间"
    )

    # 关系
    case: Mapped["Case"] = relationship("Case", back_populates="executions")

    def __repr__(self) -> str:
        return f"<CaseExecution(id={self.id}, case_id={self.case_id}, status={self.status})>"
