"""CustomColumn 模型 — Case 表格自定义列定义。"""

from datetime import datetime
from sqlalchemy import String, Boolean, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class CustomColumn(Base):
    __tablename__ = "custom_columns"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="列显示名称")
    field_key: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="字段标识符(英文)")
    column_type: Mapped[str] = mapped_column(String(20), default="text", comment="类型: text/number/select")
    options: Mapped[str | None] = mapped_column(String(500), default=None, comment="下拉选项JSON")
    is_required: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否必填")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, comment="排序顺序")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), comment="创建时间")

    def __repr__(self) -> str:
        return f"<CustomColumn(id={self.id}, name={self.name}, type={self.column_type})>"
