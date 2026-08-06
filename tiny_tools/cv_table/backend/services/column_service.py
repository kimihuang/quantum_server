"""Column Service — 自定义列业务逻辑。"""

import json
from sqlalchemy.orm import Session

from ..models.custom_column import CustomColumn
from ..repositories.column_repo import ColumnRepository
from ..core.exceptions import NotFoundError, BusinessError


def _parse_options(raw):
    """将选项字符串转为 JSON 存储。支持逗号分隔或 JSON 数组。"""
    if not raw:
        return None
    if isinstance(raw, list):
        return json.dumps(raw, ensure_ascii=False)
    raw = str(raw).strip()
    if not raw:
        return None
    # 尝试直接解析 JSON
    try:
        parsed = json.loads(raw)
        return json.dumps(parsed, ensure_ascii=False)
    except (json.JSONDecodeError, ValueError):
        pass
    # 逗号分隔字符串 → JSON 数组
    return json.dumps([o.strip() for o in raw.split(',') if o.strip()], ensure_ascii=False)


class ColumnService:
    def __init__(self, repo: ColumnRepository | None = None):
        self.repo = repo or ColumnRepository()

    def list_columns(self, db: Session) -> list[dict]:
        cols = self.repo.get_all(db)
        return [
            {
                "id": c.id,
                "name": c.name,
                "field_key": c.field_key,
                "column_type": c.column_type,
                "options": json.loads(c.options) if c.options else None,
                "is_required": c.is_required,
                "sort_order": c.sort_order,
                "created_at": c.created_at.isoformat() if c.created_at else "",
            }
            for c in cols
        ]

    def create_column(self, db: Session, data: dict) -> dict:
        # 检查 field_key 唯一性
        existing = self.repo.get_by_key(db, data["field_key"])
        if existing:
            raise BusinessError(f"字段标识 '{data['field_key']}' 已存在")

        # 验证 select 类型必须有 options
        if data.get("column_type") == "select" and not data.get("options"):
            raise BusinessError("select 类型必须提供选项列表")

        # 将 options 转为 JSON 存储
        if "options" in data:
            data["options"] = _parse_options(data["options"])

        col = CustomColumn(**data)
        col = self.repo.create(db, col)
        return self._to_dict(col)

    def update_column(self, db: Session, col_id: int, data: dict) -> dict:
        col = self.repo.get_by_id(db, col_id)
        if not col:
            raise NotFoundError("CustomColumn", col_id)

        # 如果修改了 field_key，检查唯一性
        if "field_key" in data and data["field_key"] != col.field_key:
            existing = self.repo.get_by_key(db, data["field_key"])
            if existing:
                raise BusinessError(f"字段标识 '{data['field_key']}' 已存在")

        for key, value in data.items():
            if value is not None:
                if key == "options":
                    value = _parse_options(value)
                setattr(col, key, value)
        col = self.repo.update(db, col)
        return self._to_dict(col)

    def delete_column(self, db: Session, col_id: int) -> None:
        col = self.repo.get_by_id(db, col_id)
        if not col:
            raise NotFoundError("CustomColumn", col_id)
        self.repo.delete(db, col)

    @staticmethod
    def _to_dict(col: CustomColumn) -> dict:
        opts = None
        if col.options:
            try:
                opts = json.loads(col.options)
            except (json.JSONDecodeError, ValueError):
                # 兜底：逗号分隔
                opts = [o.strip() for o in str(col.options).split(',') if o.strip()]
        return {
            "id": col.id,
            "name": col.name,
            "field_key": col.field_key,
            "column_type": col.column_type,
            "options": opts,
            "is_required": col.is_required,
            "sort_order": col.sort_order,
            "created_at": col.created_at.isoformat() if col.created_at else "",
        }
