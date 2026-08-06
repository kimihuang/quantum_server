"""公共依赖注入。"""

from ..core.config import config
from ..services.sys_service import SysService
from ..services.ip_service import IPService
from ..services.case_service import CaseService
from ..services.stats_service import StatsService


def get_sys_service() -> SysService:
    return SysService()


def get_ip_service() -> IPService:
    return IPService()


def get_case_service() -> CaseService:
    return CaseService()


def get_stats_service() -> StatsService:
    return StatsService()


def get_config() -> dict:
    return {
        "priorities": config.get("case.priorities", []),
        "statuses": config.get("case.statuses", []),
        "status_transitions": config.get("case.status_transitions", {}),
    }
