"""Scenario 路由。"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...schemas.scenario import ScenarioCreate, ScenarioUpdate
from ...services.scenario_service import ScenarioService
from ..deps import get_scenario_service

router = APIRouter(prefix="/scenarios", tags=["Scenarios"])


@router.get("")
def list_scenarios(
    db: Session = Depends(get_db),
    service: ScenarioService = Depends(get_scenario_service),
):
    """获取所有场景列表。"""
    scenarios = service.list_scenarios(db)
    return [
        {
            "id": s.id,
            "name": s.name,
            "description": s.description,
            "created_at": s.created_at.isoformat() if s.created_at else "",
        }
        for s in scenarios
    ]


@router.post("")
def create_scenario(
    data: ScenarioCreate,
    db: Session = Depends(get_db),
    service: ScenarioService = Depends(get_scenario_service),
):
    """创建场景。"""
    return service.create_scenario(db, data.name, data.description)


@router.put("/{scenario_id}")
def update_scenario(
    scenario_id: int,
    data: ScenarioUpdate,
    db: Session = Depends(get_db),
    service: ScenarioService = Depends(get_scenario_service),
):
    """更新场景。"""
    return service.update_scenario(db, scenario_id, data.name, data.description)


@router.delete("/{scenario_id}")
def delete_scenario(
    scenario_id: int,
    db: Session = Depends(get_db),
    service: ScenarioService = Depends(get_scenario_service),
):
    """删除场景。"""
    service.delete_scenario(db, scenario_id)
    return {"message": "删除成功"}
