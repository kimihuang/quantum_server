"""Subsystem Repository — 子系统数据访问。"""

from sqlalchemy.orm import Session

from ..models.subsystem import Subsystem
from ..models.ip import IP


class SubsystemRepository:
    """子系统数据访问。"""

    def get_all(self, db: Session, ip_id: int | None = None) -> list[Subsystem]:
        """获取子系统列表，可按 IP 筛选。"""
        query = db.query(Subsystem).join(IP)
        if ip_id is not None:
            query = query.filter(Subsystem.ip_id == ip_id)
        return query.order_by(Subsystem.ip_id, Subsystem.id).all()

    def get_by_id(self, db: Session, sub_id: int) -> Subsystem | None:
        """根据 ID 获取子系统。"""
        return db.query(Subsystem).filter(Subsystem.id == sub_id).first()

    def get_by_name_and_ip(self, db: Session, name: str, ip_id: int) -> Subsystem | None:
        """根据名称和 IP 获取子系统。"""
        return db.query(Subsystem).filter(
            Subsystem.name == name, Subsystem.ip_id == ip_id
        ).first()

    def create(self, db: Session, subsystem: Subsystem) -> Subsystem:
        """创建子系统。"""
        db.add(subsystem)
        db.commit()
        db.refresh(subsystem)
        return subsystem

    def update(self, db: Session, subsystem: Subsystem) -> Subsystem:
        """更新子系统。"""
        db.commit()
        db.refresh(subsystem)
        return subsystem

    def delete(self, db: Session, subsystem: Subsystem) -> None:
        """删除子系统。"""
        db.delete(subsystem)
        db.commit()
