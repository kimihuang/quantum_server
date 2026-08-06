"""Scenario Service — 场景业务逻辑。"""

from sqlalchemy.orm import Session

from ..models.scenario import Scenario
from ..repositories.scenario_repo import ScenarioRepository
from ..core.exceptions import NotFoundError, BusinessError


class ScenarioService:
    """场景业务服务。"""

    def __init__(self, repo: ScenarioRepository | None = None):
        self.repo = repo or ScenarioRepository()

    def list_scenarios(self, db: Session) -> list[Scenario]:
        """获取所有场景。"""
        return self.repo.get_all(db)

    def create_scenario(self, db: Session, name: str, description: str = "") -> Scenario:
        """创建场景。"""
        existing = self.repo.get_by_name(db, name)
        if existing:
            raise BusinessError(f"场景 '{name}' 已存在")
        scenario = Scenario(name=name, description=description)
        return self.repo.create(db, scenario)

    def update_scenario(self, db: Session, scenario_id: int,
                        name: str | None = None, description: str | None = None) -> Scenario:
        """更新场景。"""
        scenario = self.repo.get_by_id(db, scenario_id)
        if not scenario:
            raise NotFoundError("Scenario", scenario_id)

        if name is not None:
            existing = self.repo.get_by_name(db, name)
            if existing and existing.id != scenario_id:
                raise BusinessError(f"场景 '{name}' 已存在")
            scenario.name = name
        if description is not None:
            scenario.description = description

        return self.repo.update(db, scenario)

    def delete_scenario(self, db: Session, scenario_id: int) -> None:
        """删除场景。"""
        scenario = self.repo.get_by_id(db, scenario_id)
        if not scenario:
            raise NotFoundError("Scenario", scenario_id)
        self.repo.delete(db, scenario)
