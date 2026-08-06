"""Subsystem 路由。"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...schemas.subsystem import SubsystemCreate, SubsystemUpdate
from ...services.subsystem_service import SubsystemService
from ..deps import get_subsystem_service

router = APIRouter(prefix="/subsystems", tags=["Subsystems"])


@router.get("")
def list_subsystems(
    ip_id: int | None = Query(None, description="按 IP 筛选"),
    db: Session = Depends(get_db),
    service: SubsystemService = Depends(get_subsystem_service),
):
    """获取子系统列表。"""
    return service.list_subsystems(db, ip_id)


@router.post("")
def create_subsystem(
    data: SubsystemCreate,
    db: Session = Depends(get_db),
    service: SubsystemService = Depends(get_subsystem_service),
):
    """创建子系统。"""
    return service.create_subsystem(db, data.name, data.ip_id, data.description)


@router.put("/{sub_id}")
def update_subsystem(
    sub_id: int,
    data: SubsystemUpdate,
    db: Session = Depends(get_db),
    service: SubsystemService = Depends(get_subsystem_service),
):
    """更新子系统。"""
    return service.update_subsystem(db, sub_id, data.name, data.ip_id, data.description)


@router.delete("/{sub_id}")
def delete_subsystem(
    sub_id: int,
    db: Session = Depends(get_db),
    service: SubsystemService = Depends(get_subsystem_service),
):
    """删除子系统。"""
    service.delete_subsystem(db, sub_id)
    return {"message": "删除成功"}
