"""Case Service — Case 业务逻辑，简化版（无子系统/场景）。"""

import csv
import io
from typing import Optional
from sqlalchemy.orm import Session

from ..models.case import Case
from ..models.ip import IP as IPModel
from ..models.sys import Sys as SysModel
from ..models.case_execution import CaseExecution
from ..repositories.case_repo import CaseRepository
from ..repositories.ip_repo import IPRepository
from ..core.config import config
from ..core.exceptions import NotFoundError, BusinessError


class StatusMachine:
    def __init__(self):
        self.transitions: dict[str, list[str]] = config.get("case.status_transitions", {})

    def can_transition(self, from_status: str, to_status: str) -> bool:
        return to_status in self.transitions.get(from_status, [])

    def get_allowed(self, current_status: str) -> list[str]:
        return self.transitions.get(current_status, [])


class CaseService:
    def __init__(self, repo: CaseRepository | None = None, ip_repo: IPRepository | None = None):
        self.repo = repo or CaseRepository()
        self.ip_repo = ip_repo or IPRepository()
        self.status_machine = StatusMachine()

    def _to_response(self, case: Case) -> dict:
        return {
            "id": case.id,
            "name": case.name,
            "ip_id": case.ip_id,
            "ip_name": case.ip.name if case.ip else "",
            "sys_id": case.ip.sys_id if case.ip else 0,
            "sys_name": case.ip.sys.name if case.ip and case.ip.sys else "",
            "description": case.description,
            "priority": case.priority,
            "status": case.status,
            "owner": case.owner,
            "custom_fields": case.custom_fields,
            "created_at": case.created_at.isoformat() if case.created_at else "",
            "updated_at": case.updated_at.isoformat() if case.updated_at else "",
        }

    def list_cases(self, db: Session, filters: dict) -> dict:
        items, total = self.repo.find_by_filter(db, **filters)
        page = filters.get("page", 1)
        page_size = filters.get("page_size", 20)
        pages = (total + page_size - 1) // page_size if total > 0 else 1
        return {
            "items": [self._to_response(c) for c in items],
            "total": total, "page": page, "page_size": page_size, "pages": pages,
        }

    def get_case(self, db: Session, case_id: int) -> dict:
        case = self.repo.get_by_id(db, case_id)
        if not case:
            raise NotFoundError("Case", case_id)
        return self._to_response(case)

    def create_case(self, db: Session, data: dict) -> dict:
        if not self.ip_repo.get_by_id(db, data["ip_id"]):
            raise NotFoundError("IP", data["ip_id"])
        case = Case(**data)
        case = self.repo.create(db, case)
        return self._to_response(case)

    def update_case(self, db: Session, case_id: int, data: dict) -> dict:
        case = self.repo.get_by_id(db, case_id)
        if not case:
            raise NotFoundError("Case", case_id)
        # 如果更新了 ip_id，验证新 IP 是否存在
        if "ip_id" in data and data["ip_id"] is not None and data["ip_id"] != case.ip_id:
            if not self.ip_repo.get_by_id(db, data["ip_id"]):
                raise NotFoundError("IP", data["ip_id"])
        for key, value in data.items():
            if value is not None:
                setattr(case, key, value)
        case = self.repo.update(db, case)
        return self._to_response(case)

    def delete_case(self, db: Session, case_id: int) -> None:
        case = self.repo.get_by_id(db, case_id)
        if not case:
            raise NotFoundError("Case", case_id)
        self.repo.delete(db, case)

    def update_status(self, db: Session, case_id: int, status: str, executor: str = "", log: str = "") -> dict:
        case = self.repo.get_by_id(db, case_id)
        if not case:
            raise NotFoundError("Case", case_id)
        if not self.status_machine.can_transition(case.status, status):
            allowed = self.status_machine.get_allowed(case.status)
            raise BusinessError(f"不允许的状态转换: {case.status} → {status}，允许: {', '.join(allowed)}")
        case.status = status
        case = self.repo.update(db, case)
        self.repo.add_execution(db, CaseExecution(case_id=case_id, status=status, log=log, executor=executor))
        return self._to_response(case)

    def get_executions(self, db: Session, case_id: int) -> list[dict]:
        return [
            {"id": e.id, "case_id": e.case_id, "status": e.status,
             "log": e.log, "executor": e.executor,
             "executed_at": e.executed_at.isoformat() if e.executed_at else ""}
            for e in self.repo.get_executions(db, case_id)
        ]

    def batch_update(self, db: Session, ids: list[int], **kwargs) -> int:
        return self.repo.batch_update_status(db, ids, **kwargs)

    def batch_delete(self, db: Session, ids: list[int]) -> int:
        return self.repo.batch_delete(db, ids)

    def export_csv(self, db: Session, filters: dict) -> str:
        items, _ = self.repo.find_by_filter(db, **filters)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["名称", "SYS", "IP", "优先级", "状态", "负责人", "描述", "创建时间", "更新时间"])
        for case in items:
            writer.writerow([
                case.name,
                case.ip.sys.name if case.ip and case.ip.sys else "",
                case.ip.name if case.ip else "",
                case.priority, case.status, case.owner, case.description,
                case.created_at.isoformat() if case.created_at else "",
                case.updated_at.isoformat() if case.updated_at else "",
            ])
        return output.getvalue()

    def import_csv(self, db: Session, content: str) -> dict:
        reader = csv.DictReader(io.StringIO(content))
        created = 0
        skipped = 0
        errors = []
        for row_num, row in enumerate(reader, start=2):
            try:
                name = row.get("名称", "").strip()
                sys_name = row.get("SYS", "").strip()
                ip_name = row.get("IP", "").strip()
                if not name or not ip_name:
                    skipped += 1
                    continue

                # 查找或创建 SYS
                from ..repositories.sys_repo import SysRepository
                sys_repo = SysRepository()
                sys = sys_repo.get_by_name(db, sys_name)
                if not sys:
                    sys = sys_repo.create(db, SysModel(name=sys_name))

                # 查找或创建 IP
                ip = self.ip_repo.get_by_name_and_sys(db, ip_name, sys.id)
                if not ip:
                    ip = self.ip_repo.create(db, IPModel(name=ip_name, sys_id=sys.id))

                # 检查重复：同一 IP 下同名 Case 不导入
                existing_case = self.repo.get_by_name_and_ip(db, name, ip.id)
                if existing_case:
                    skipped += 1
                    continue

                case = Case(
                    name=name, ip_id=ip.id,
                    priority=row.get("优先级", "P2").strip(),
                    status=row.get("状态", "not_run").strip(),
                    owner=row.get("负责人", "").strip(),
                    description=row.get("描述", "").strip(),
                )
                self.repo.create(db, case)
                created += 1
            except Exception as e:
                errors.append(f"第 {row_num} 行: {str(e)}")
                skipped += 1
        return {"created": created, "skipped": skipped, "errors": errors}
