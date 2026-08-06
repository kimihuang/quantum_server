"""Case Repository — Case 数据访问，按 IP/SYS 筛选。"""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, case as sql_case

from ..models.case import Case
from ..models.ip import IP
from ..models.sys import Sys
from ..models.case_execution import CaseExecution


class CaseRepository:
    """Case 数据访问。"""

    def _base_query(self, db: Session):
        return db.query(Case).join(IP, Case.ip_id == IP.id).join(Sys, IP.sys_id == Sys.id)

    def find_by_filter(
        self,
        db: Session,
        sys_id: Optional[int] = None,
        ip_id: Optional[int] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Case], int]:
        query = self._base_query(db)

        if sys_id is not None:
            query = query.filter(IP.sys_id == sys_id)
        if ip_id is not None:
            query = query.filter(Case.ip_id == ip_id)
        if status:
            query = query.filter(Case.status == status)
        if priority:
            query = query.filter(Case.priority == priority)
        if keyword:
            query = query.filter(Case.name.contains(keyword))

        total = query.count()
        items = (
            query.order_by(Case.updated_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

    def get_by_id(self, db: Session, case_id: int) -> Case | None:
        return self._base_query(db).filter(Case.id == case_id).first()

    def get_by_name_and_ip(self, db: Session, name: str, ip_id: int) -> Case | None:
        return db.query(Case).filter(Case.name == name, Case.ip_id == ip_id).first()

    def get_by_ids(self, db: Session, ids: list[int]) -> list[Case]:
        return db.query(Case).filter(Case.id.in_(ids)).all()

    def create(self, db: Session, case: Case) -> Case:
        db.add(case)
        db.commit()
        db.refresh(case)
        return case

    def update(self, db: Session, case: Case) -> Case:
        db.commit()
        db.refresh(case)
        return case

    def delete(self, db: Session, case: Case) -> None:
        db.delete(case)
        db.commit()

    def batch_update_status(self, db: Session, ids: list[int], **kwargs) -> int:
        if not kwargs:
            return 0
        count = db.query(Case).filter(Case.id.in_(ids)).update(kwargs, synchronize_session="fetch")
        db.commit()
        return count

    def batch_delete(self, db: Session, ids: list[int]) -> int:
        count = db.query(Case).filter(Case.id.in_(ids)).delete(synchronize_session="fetch")
        db.commit()
        return count

    def add_execution(self, db: Session, execution: CaseExecution) -> CaseExecution:
        db.add(execution)
        db.commit()
        db.refresh(execution)
        return execution

    def get_executions(self, db: Session, case_id: int) -> list[CaseExecution]:
        return (
            db.query(CaseExecution)
            .filter(CaseExecution.case_id == case_id)
            .order_by(CaseExecution.executed_at.desc())
            .all()
        )

    def get_overview_stats(self, db: Session) -> dict:
        stats = (
            db.query(
                func.count(Case.id).label("total"),
                func.sum(sql_case((Case.status == "pass", 1), else_=0)).label("pass_count"),
                func.sum(sql_case((Case.status == "fail", 1), else_=0)).label("fail_count"),
                func.sum(sql_case((Case.status == "not_run", 1), else_=0)).label("not_run_count"),
                func.sum(sql_case((Case.status == "blocked", 1), else_=0)).label("blocked_count"),
                func.sum(sql_case((Case.status == "skip", 1), else_=0)).label("skip_count"),
            ).first()
        )
        return {
            "total": stats.total or 0,
            "pass_count": stats.pass_count or 0,
            "fail_count": stats.fail_count or 0,
            "not_run_count": stats.not_run_count or 0,
            "blocked_count": stats.blocked_count or 0,
            "skip_count": stats.skip_count or 0,
        }

    def get_stats_by_sys(self, db: Session) -> list[dict]:
        return (
            db.query(
                Sys.id.label("group_id"),
                Sys.name.label("group_name"),
                func.count(Case.id).label("total"),
                func.sum(sql_case((Case.status == "pass", 1), else_=0)).label("pass_count"),
                func.sum(sql_case((Case.status == "fail", 1), else_=0)).label("fail_count"),
                func.sum(sql_case((Case.status == "blocked", 1), else_=0)).label("blocked_count"),
            )
            .outerjoin(IP, IP.sys_id == Sys.id)
            .outerjoin(Case, Case.ip_id == IP.id)
            .group_by(Sys.id)
            .order_by(Sys.id)
            .all()
        )

    def get_stats_by_ip(self, db: Session, sys_id: Optional[int] = None) -> list[dict]:
        query = (
            db.query(
                IP.id.label("group_id"),
                IP.name.label("group_name"),
                func.count(Case.id).label("total"),
                func.sum(sql_case((Case.status == "pass", 1), else_=0)).label("pass_count"),
                func.sum(sql_case((Case.status == "fail", 1), else_=0)).label("fail_count"),
                func.sum(sql_case((Case.status == "blocked", 1), else_=0)).label("blocked_count"),
            )
            .outerjoin(Case, Case.ip_id == IP.id)
        )
        if sys_id is not None:
            query = query.filter(IP.sys_id == sys_id)
        return query.group_by(IP.id).order_by(IP.id).all()
