"""Scenario Repository — 场景数据访问。"""

from sqlalchemy.orm import Session

from ..models.scenario import Scenario


class ScenarioRepository:
    """场景数据访问。"""

    def get_all(self, db: Session) -> list[Scenario]:
        """获取所有场景。"""
        return db.query(Scenario).order_by(Scenario.id).all()

    def get_by_id(self, db: Session, scenario_id: int) -> Scenario | None:
        """根据 ID 获取场景。"""
        return db.query(Scenario).filter(Scenario.id == scenario_id).first()

    def get_by_name(self, db: Session, name: str) -> Scenario | None:
        """根据名称获取场景。"""
        return db.query(Scenario).filter(Scenario.name == name).first()

    def create(self, db: Session, scenario: Scenario) -> Scenario:
        """创建场景。"""
        db.add(scenario)
        db.commit()
        db.refresh(scenario)
        return scenario

    def update(self, db: Session, scenario: Scenario) -> Scenario:
        """更新场景。"""
        db.commit()
        db.refresh(scenario)
        return scenario

    def delete(self, db: Session, scenario: Scenario) -> None:
        """删除场景。"""
        db.delete(scenario)
        db.commit()
