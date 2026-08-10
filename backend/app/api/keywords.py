"""
关键词管理接口
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth_deps import require_staff, require_admin
from app.models.keyword import Keyword
from app.schemas.keyword import KeywordCreate, KeywordUpdate, KeywordResponse

router = APIRouter(prefix="/keywords", tags=["关键词管理"])


@router.get("")
def list_keywords(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    keyword: str | None = Query(None),
    status: int | None = Query(None),
    db: Session = Depends(get_db),
    _=Depends(require_staff),
):
    q = db.query(Keyword)
    if keyword:
        q = q.filter(Keyword.keyword.contains(keyword))
    if status is not None:
        q = q.filter(Keyword.status == status)
    q = q.order_by(Keyword.created_at.desc())
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return {"items": items, "total": total}


@router.get("/all", response_model=list[KeywordResponse])
def all_keywords(db: Session = Depends(get_db), _=Depends(require_staff)):
    """获取所有启用关键词（采集用）"""
    return db.query(Keyword).filter(Keyword.status == 1).all()


@router.post("", response_model=KeywordResponse)
def create_keyword(
    req: KeywordCreate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    exist = db.query(Keyword).filter(Keyword.keyword == req.keyword).first()
    if exist:
        raise HTTPException(status_code=400, detail="关键词已存在")
    kw = Keyword(**req.model_dump())
    db.add(kw)
    db.commit()
    db.refresh(kw)
    return kw


@router.put("/{kw_id}", response_model=KeywordResponse)
def update_keyword(
    kw_id: int,
    req: KeywordUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    kw = db.query(Keyword).filter(Keyword.id == kw_id).first()
    if not kw:
        raise HTTPException(status_code=404, detail="关键词不存在")
    for k, v in req.model_dump(exclude_unset=True).items():
        setattr(kw, k, v)
    db.commit()
    db.refresh(kw)
    return kw


@router.delete("/{kw_id}")
def delete_keyword(
    kw_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    kw = db.query(Keyword).filter(Keyword.id == kw_id).first()
    if not kw:
        raise HTTPException(status_code=404, detail="关键词不存在")
    db.delete(kw)
    db.commit()
    return {"message": "删除成功"}
