"""Sys 路由。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...schemas.sys import SysCreate, SysUpdate
from ...services.sys_service import SysService
from ..deps import get_sys_service

router = APIRouter(prefix="/systems", tags=["Systems"])


def get_sys_service():
    return SysService()


@router.get("")
def list_systems(db: Session = Depends(get_db)):
    service = SysService()
    return service.list_systems(db)


@router.post("")
def create_sys(data: SysCreate, db: Session = Depends(get_db)):
    service = SysService()
    return service.create_sys(db, data.name, data.description)


@router.put("/{sys_id}")
def update_sys(sys_id: int, data: SysUpdate, db: Session = Depends(get_db)):
    service = SysService()
    return service.update_sys(db, sys_id, name=data.name, description=data.description)


@router.delete("/{sys_id}")
def delete_sys(sys_id: int, db: Session = Depends(get_db)):
    service = SysService()
    service.delete_sys(db, sys_id)
    return {"message": "删除成功"}
