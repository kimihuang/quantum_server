"""IP 路由。"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...schemas.ip import IPCreate, IPUpdate
from ...services.ip_service import IPService

router = APIRouter(prefix="/ips", tags=["IPs"])


@router.get("")
def list_ips(
    sys_id: int | None = Query(None),
    db: Session = Depends(get_db),
):
    return IPService().list_ips(db, sys_id)


@router.post("")
def create_ip(data: IPCreate, db: Session = Depends(get_db)):
    return IPService().create_ip(db, data.name, data.sys_id, data.description)


@router.put("/{ip_id}")
def update_ip(ip_id: int, data: IPUpdate, db: Session = Depends(get_db)):
    return IPService().update_ip(db, ip_id, **data.model_dump(exclude_unset=True))


@router.delete("/{ip_id}")
def delete_ip(ip_id: int, db: Session = Depends(get_db)):
    IPService().delete_ip(db, ip_id)
    return {"message": "删除成功"}
