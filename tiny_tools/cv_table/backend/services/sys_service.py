"""Sys Service — 系统业务逻辑。"""

from sqlalchemy.orm import Session

from ..models.sys import Sys
from ..repositories.sys_repo import SysRepository
from ..core.exceptions import NotFoundError, BusinessError


class SysService:
    """系统业务服务。"""

    def __init__(self, repo: SysRepository | None = None):
        self.repo = repo or SysRepository()

    def list_systems(self, db: Session) -> list[dict]:
        systems = self.repo.get_all(db)
        return [
            {
                "id": s.id,
                "name": s.name,
                "description": s.description,
                "created_at": s.created_at,
                "ip_count": self.repo.get_ip_count(db, s.id),
                "case_count": self.repo.get_case_count(db, s.id),
            }
            for s in systems
        ]

    def create_sys(self, db: Session, name: str, description: str = "") -> Sys:
        existing = self.repo.get_by_name(db, name)
        if existing:
            raise BusinessError(f"SYS '{name}' 已存在")
        return self.repo.create(db, Sys(name=name, description=description))

    def update_sys(self, db: Session, sys_id: int, **kwargs) -> Sys:
        sys = self.repo.get_by_id(db, sys_id)
        if not sys:
            raise NotFoundError("SYS", sys_id)
        for key, value in kwargs.items():
            if value is not None:
                setattr(sys, key, value)
        return self.repo.update(db, sys)

    def delete_sys(self, db: Session, sys_id: int) -> None:
        sys = self.repo.get_by_id(db, sys_id)
        if not sys:
            raise NotFoundError("SYS", sys_id)
        ip_count = self.repo.get_ip_count(db, sys_id)
        if ip_count > 0:
            raise BusinessError(f"SYS 下存在 {ip_count} 个 IP，无法删除")
        self.repo.delete(db, sys)
