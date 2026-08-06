"""Subsystem Service — 子系统业务逻辑。"""

from sqlalchemy.orm import Session

from ..models.subsystem import Subsystem
from ..repositories.subsystem_repo import SubsystemRepository
from ..repositories.ip_repo import IPRepository
from ..core.exceptions import NotFoundError, BusinessError


class SubsystemService:
    """子系统业务服务。"""

    def __init__(self, repo: SubsystemRepository | None = None, ip_repo: IPRepository | None = None):
        self.repo = repo or SubsystemRepository()
        self.ip_repo = ip_repo or IPRepository()

    def list_subsystems(self, db: Session, ip_id: int | None = None) -> list[dict]:
        """获取子系统列表。"""
        subsystems = self.repo.get_all(db, ip_id)
        result = []
        for sub in subsystems:
            result.append({
                "id": sub.id,
                "name": sub.name,
                "ip_id": sub.ip_id,
                "ip_name": sub.ip.name if sub.ip else "",
                "description": sub.description,
                "created_at": sub.created_at,
            })
        return result

    def create_subsystem(self, db: Session, name: str, ip_id: int, description: str = "") -> Subsystem:
        """创建子系统。"""
        ip = self.ip_repo.get_by_id(db, ip_id)
        if not ip:
            raise NotFoundError("IP", ip_id)

        existing = self.repo.get_by_name_and_ip(db, name, ip_id)
        if existing:
            raise BusinessError(f"子系统 '{name}' 在该 IP 下已存在")

        subsystem = Subsystem(name=name, ip_id=ip_id, description=description)
        return self.repo.create(db, subsystem)

    def update_subsystem(self, db: Session, sub_id: int, name: str | None = None,
                         ip_id: int | None = None, description: str | None = None) -> Subsystem:
        """更新子系统。"""
        subsystem = self.repo.get_by_id(db, sub_id)
        if not subsystem:
            raise NotFoundError("Subsystem", sub_id)

        if ip_id is not None:
            ip = self.ip_repo.get_by_id(db, ip_id)
            if not ip:
                raise NotFoundError("IP", ip_id)
            subsystem.ip_id = ip_id

        if name is not None:
            existing = self.repo.get_by_name_and_ip(db, name, subsystem.ip_id)
            if existing and existing.id != sub_id:
                raise BusinessError(f"子系统 '{name}' 在该 IP 下已存在")
            subsystem.name = name
        if description is not None:
            subsystem.description = description

        return self.repo.update(db, subsystem)

    def delete_subsystem(self, db: Session, sub_id: int) -> None:
        """删除子系统。"""
        subsystem = self.repo.get_by_id(db, sub_id)
        if not subsystem:
            raise NotFoundError("Subsystem", sub_id)
        self.repo.delete(db, subsystem)
