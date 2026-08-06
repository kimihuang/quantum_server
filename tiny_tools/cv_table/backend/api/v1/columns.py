"""CustomColumn 路由 — 自定义列 CRUD。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...schemas.column import CustomColumnCreate, CustomColumnUpdate
from ...services.column_service import ColumnService

router = APIRouter(prefix="/columns", tags=["CustomColumns"])


@router.get("")
def list_columns(db: Session = Depends(get_db)):
    return ColumnService().list_columns(db)


@router.post("")
def create_column(data: CustomColumnCreate, db: Session = Depends(get_db)):
    return ColumnService().create_column(db, data.model_dump())


@router.put("/{col_id}")
def update_column(col_id: int, data: CustomColumnUpdate, db: Session = Depends(get_db)):
    return ColumnService().update_column(db, col_id, data.model_dump(exclude_unset=True))


@router.delete("/{col_id}")
def delete_column(col_id: int, db: Session = Depends(get_db)):
    ColumnService().delete_column(db, col_id)
    return {"message": "删除成功"}
