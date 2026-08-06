"""CustomColumn Repository — 自定义列数据访问。"""

from sqlalchemy.orm import Session

from ..models.custom_column import CustomColumn


class ColumnRepository:
    """自定义列数据访问。"""

    def get_all(self, db: Session) -> list[CustomColumn]:
        return db.query(CustomColumn).order_by(CustomColumn.sort_order, CustomColumn.id).all()

    def get_by_id(self, db: Session, col_id: int) -> CustomColumn | None:
        return db.query(CustomColumn).filter(CustomColumn.id == col_id).first()

    def get_by_key(self, db: Session, field_key: str) -> CustomColumn | None:
        return db.query(CustomColumn).filter(CustomColumn.field_key == field_key).first()

    def create(self, db: Session, col: CustomColumn) -> CustomColumn:
        db.add(col)
        db.commit()
        db.refresh(col)
        return col

    def update(self, db: Session, col: CustomColumn) -> CustomColumn:
        db.commit()
        db.refresh(col)
        return col

    def delete(self, db: Session, col: CustomColumn) -> None:
        db.delete(col)
        db.commit()
