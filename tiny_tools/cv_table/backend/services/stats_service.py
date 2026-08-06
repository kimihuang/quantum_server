"""Stats Service — 统计（按 SYS/IP 维度）。"""

from typing import Optional
from sqlalchemy.orm import Session
from ..repositories.case_repo import CaseRepository


class StatsService:
    def __init__(self, repo: CaseRepository | None = None):
        self.repo = repo or CaseRepository()

    def _pass_rate(self, total: int, pass_count: int) -> float:
        return round(pass_count / total * 100, 1) if total > 0 else 0.0

    def get_overview(self, db: Session) -> dict:
        stats = self.repo.get_overview_stats(db)
        stats["pass_rate"] = self._pass_rate(stats["total"], stats["pass_count"])
        return stats

    def get_by_sys(self, db: Session) -> list[dict]:
        rows = self.repo.get_stats_by_sys(db)
        return [
            {**dict(row._mapping), "pass_rate": self._pass_rate(row.total or 0, row.pass_count or 0)}
            for row in rows
        ]

    def get_by_ip(self, db: Session, sys_id: Optional[int] = None) -> list[dict]:
        rows = self.repo.get_stats_by_ip(db, sys_id)
        return [
            {**dict(row._mapping), "pass_rate": self._pass_rate(row.total or 0, row.pass_count or 0)}
            for row in rows
        ]
