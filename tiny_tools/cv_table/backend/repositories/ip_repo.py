"""IP Repository — IP 数据访问，按 SYS 组织。"""

from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models.ip import IP
from ..models.sys import Sys
from ..models.case import Case


class IPRepository:
    """IP 数据访问。"""

    def get_all(self, db: Session, sys_id: int | None = None) -> list[IP]:
        query = db.query(IP).join(Sys)
        if sys_id is not None:
            query = query.filter(IP.sys_id == sys_id)
        return query.order_by(IP.sys_id, IP.id).all()

    def get_by_id(self, db: Session, ip_id: int) -> IP | None:
        return db.query(IP).filter(IP.id == ip_id).first()

    def get_by_name_and_sys(self, db: Session, name: str, sys_id: int) -> IP | None:
        return db.query(IP).filter(IP.name == name, IP.sys_id == sys_id).first()

    def create(self, db: Session, ip: IP) -> IP:
        db.add(ip)
        db.commit()
        db.refresh(ip)
        return ip

    def update(self, db: Session, ip: IP) -> IP:
        db.commit()
        db.refresh(ip)
        return ip

    def delete(self, db: Session, ip: IP) -> None:
        db.delete(ip)
        db.commit()

    def get_case_count(self, db: Session, ip_id: int) -> int:
        return db.query(func.count(Case.id)).filter(Case.ip_id == ip_id).scalar()
