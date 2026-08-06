"""Case 路由。"""

from fastapi import APIRouter, Depends, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...schemas.case import CaseCreate, CaseUpdate, CaseStatusUpdate, CaseBatchUpdate
from ...services.case_service import CaseService

router = APIRouter(prefix="/cases", tags=["Cases"])


@router.get("")
def list_cases(
    sys_id: int | None = Query(None),
    ip_id: int | None = Query(None),
    status: str | None = Query(None),
    priority: str | None = Query(None),
    keyword: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    filters = {
        "sys_id": sys_id, "ip_id": ip_id, "status": status,
        "priority": priority, "keyword": keyword, "page": page, "page_size": page_size,
    }
    return CaseService().list_cases(db, filters)


@router.get("/export/csv")
def export_csv(
    sys_id: int | None = Query(None),
    ip_id: int | None = Query(None),
    status: str | None = Query(None),
    db: Session = Depends(get_db),
):
    filters = {"sys_id": sys_id, "ip_id": ip_id, "status": status, "page": 1, "page_size": 1000}
    csv_content = CaseService().export_csv(db, filters)
    from io import BytesIO
    output = BytesIO(csv_content.encode("utf-8-sig"))
    return StreamingResponse(
        output, media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=cases_export.csv"},
    )


@router.post("/import/csv")
async def import_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    return CaseService().import_csv(db, content.decode("utf-8-sig"))


@router.get("/{case_id}")
def get_case(case_id: int, db: Session = Depends(get_db)):
    return CaseService().get_case(db, case_id)


@router.post("")
def create_case(data: CaseCreate, db: Session = Depends(get_db)):
    return CaseService().create_case(db, data.model_dump())


@router.put("/{case_id}")
def update_case(case_id: int, data: CaseUpdate, db: Session = Depends(get_db)):
    return CaseService().update_case(db, case_id, data.model_dump(exclude_unset=True))


@router.delete("/{case_id}")
def delete_case(case_id: int, db: Session = Depends(get_db)):
    CaseService().delete_case(db, case_id)
    return {"message": "删除成功"}


@router.put("/{case_id}/status")
def update_status(case_id: int, data: CaseStatusUpdate, db: Session = Depends(get_db)):
    return CaseService().update_status(db, case_id, data.status, data.executor, data.log)


@router.get("/{case_id}/executions")
def get_executions(case_id: int, db: Session = Depends(get_db)):
    return CaseService().get_executions(db, case_id)


@router.post("/batch/update")
def batch_update(data: CaseBatchUpdate, db: Session = Depends(get_db)):
    updates = {}
    if data.status is not None: updates["status"] = data.status
    if data.priority is not None: updates["priority"] = data.priority
    if data.owner is not None: updates["owner"] = data.owner
    return {"count": CaseService().batch_update(db, data.ids, **updates)}


@router.post("/batch/delete")
def batch_delete(ids: list[int], db: Session = Depends(get_db)):
    return {"count": CaseService().batch_delete(db, ids)}
