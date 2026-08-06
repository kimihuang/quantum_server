"""IP Service — IP 业务逻辑。"""

from sqlalchemy.orm import Session

from ..models.ip import IP
from ..repositories.ip_repo import IPRepository
from ..repositories.sys_repo import SysRepository
from ..core.exceptions import NotFoundError, BusinessError


class IPService:
    """IP 业务服务。"""

    def __init__(self, repo: IPRepository | None = None, sys_repo: SysRepository | None = None):
        self.repo = repo or IPRepository()
        self.sys_repo = sys_repo or SysRepository()

    def list_ips(self, db: Session, sys_id: int | None = None) -> list[dict]:
        ips = self.repo.get_all(db, sys_id)
        return [
            {
                "id": ip.id,
                "name": ip.name,
                "sys_id": ip.sys_id,
                "sys_name": ip.sys.name if ip.sys else "",
                "description": ip.description,
                "created_at": ip.created_at,
                "case_count": self.repo.get_case_count(db, ip.id),
            }
            for ip in ips
        ]

    def create_ip(self, db: Session, name: str, sys_id: int, description: str = "") -> IP:
        sys = self.sys_repo.get_by_id(db, sys_id)
        if not sys:
            raise NotFoundError("SYS", sys_id)
        existing = self.repo.get_by_name_and_sys(db, name, sys_id)
        if existing:
            raise BusinessError(f"IP '{name}' 在该 SYS 下已存在")
        return self.repo.create(db, IP(name=name, sys_id=sys_id, description=description))

    def update_ip(self, db: Session, ip_id: int, **kwargs) -> IP:
        ip = self.repo.get_by_id(db, ip_id)
        if not ip:
            raise NotFoundError("IP", ip_id)
        for key, value in kwargs.items():
            if value is not None:
                setattr(ip, key, value)
        return self.repo.update(db, ip)

    def delete_ip(self, db: Session, ip_id: int) -> None:
        ip = self.repo.get_by_id(db, ip_id)
        if not ip:
            raise NotFoundError("IP", ip_id)
        case_count = self.repo.get_case_count(db, ip_id)
        if case_count > 0:
            raise BusinessError(f"IP 下存在 {case_count} 个 Case，无法删除")
        self.repo.delete(db, ip)
