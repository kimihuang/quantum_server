"""Sys Repository — 系统数据访问。"""

from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models.sys import Sys
from ..models.ip import IP
from ..models.case import Case


class SysRepository:
    """系统数据访问。"""

    def get_all(self, db: Session) -> list[Sys]:
        return db.query(Sys).order_by(Sys.id).all()

    def get_by_id(self, db: Session, sys_id: int) -> Sys | None:
        return db.query(Sys).filter(Sys.id == sys_id).first()

    def get_by_name(self, db: Session, name: str) -> Sys | None:
        return db.query(Sys).filter(Sys.name == name).first()

    def create(self, db: Session, sys: Sys) -> Sys:
        db.add(sys)
        db.commit()
        db.refresh(sys)
        return sys

    def update(self, db: Session, sys: Sys) -> Sys:
        db.commit()
        db.refresh(sys)
        return sys

    def delete(self, db: Session, sys: Sys) -> None:
        db.delete(sys)
        db.commit()

    def get_ip_count(self, db: Session, sys_id: int) -> int:
        return db.query(func.count(IP.id)).filter(IP.sys_id == sys_id).scalar()

    def get_case_count(self, db: Session, sys_id: int) -> int:
        return db.query(func.count(Case.id)).join(IP).filter(IP.sys_id == sys_id).scalar()
