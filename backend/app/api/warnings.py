"""
预警记录接口
"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth_deps import get_current_user, require_staff
from app.models.warning import Warning
from app.models.user import User

router = APIRouter(prefix="/warnings", tags=["预警管理"])

LEVEL_LABELS = {"low": "低", "medium": "中", "high": "高"}
TYPE_LABELS = {
    "negative_sentiment": "负面情感",
    "sensitive_word": "敏感词命中",
    "high_frequency": "高频舆情",
}


def _fmt(w: Warning) -> dict:
    return {
        "id": w.id,
        "opinion_id": w.opinion_id,
        "warning_type": w.warning_type,
        "warning_type_label": TYPE_LABELS.get(w.warning_type, w.warning_type or "-"),
        "warning_level": w.warning_level,
        "warning_level_label": LEVEL_LABELS.get(w.warning_level, w.warning_level or "-"),
        "warning_message": w.warning_message,
        "status": w.status,
        "created_at": w.created_at,
        "handled_at": w.handled_at,
        "handler_id": w.handler_id,
    }


@router.get("")
def list_warnings(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: int | None = Query(None, description="0 未处理 1 已处理"),
    warning_level: str | None = Query(None),
    warning_type: str | None = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_staff),
):
    q = db.query(Warning)
    if status is not None:
        q = q.filter(Warning.status == status)
    if warning_level:
        q = q.filter(Warning.warning_level == warning_level)
    if warning_type:
        q = q.filter(Warning.warning_type == warning_type)
    q = q.order_by(Warning.created_at.desc())
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return {"items": [_fmt(w) for w in items], "total": total}


@router.get("/count")
def warning_count(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """未处理预警数量（管理员/用户首页均可查看）"""
    count = db.query(Warning).filter(Warning.status == 0).count()
    return {"count": count}


@router.post("/{warning_id}/handle")
def handle_warning(
    warning_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff),
):
    """标记为已处理"""
    w = db.query(Warning).filter(Warning.id == warning_id).first()
    if not w:
        raise HTTPException(status_code=404, detail="预警不存在")
    if w.status == 1:
        raise HTTPException(status_code=400, detail="预警已处理")
    w.status = 1
    w.handled_at = datetime.now()
    w.handler_id = current_user.id
    db.commit()
    return {"message": "处理成功"}
