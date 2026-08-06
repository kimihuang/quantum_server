"""Stats 路由。"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...services.stats_service import StatsService
from ..deps import get_config

router = APIRouter(prefix="/stats", tags=["Stats"])


@router.get("/config")
def get_app_config():
    return get_config()


@router.get("/overview")
def get_overview(db: Session = Depends(get_db)):
    return StatsService().get_overview(db)


@router.get("/by-sys")
def get_by_sys(db: Session = Depends(get_db)):
    return StatsService().get_by_sys(db)


@router.get("/by-ip")
def get_by_ip(sys_id: int | None = Query(None), db: Session = Depends(get_db)):
    return StatsService().get_by_ip(db, sys_id)
