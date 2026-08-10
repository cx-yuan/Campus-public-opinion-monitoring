"""
敏感词管理接口
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth_deps import require_staff
from app.models.sensitive_word import SensitiveWord
from app.models.user import User

router = APIRouter(prefix="/sensitive-words", tags=["敏感词管理"])

LEVEL_LABELS = {"high": "高", "medium": "中", "low": "低"}


class SensitiveWordCreate(BaseModel):
    word: str
    level: str = "high"
    remark: str = ""


class SensitiveWordUpdate(BaseModel):
    level: str | None = None
    status: int | None = None
    remark: str | None = None


def _fmt(w: SensitiveWord) -> dict:
    return {
        "id": w.id,
        "word": w.word,
        "level": w.level,
        "level_label": LEVEL_LABELS.get(w.level or "high", w.level or "-"),
        "status": w.status,
        "remark": w.remark,
        "created_at": w.created_at,
    }


@router.get("")
def list_words(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    keyword: str | None = Query(None),
    status: int | None = Query(None),
    level: str | None = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(require_staff),
):
    q = db.query(SensitiveWord)
    if keyword:
        q = q.filter(SensitiveWord.word.contains(keyword))
    if status is not None:
        q = q.filter(SensitiveWord.status == status)
    if level:
        q = q.filter(SensitiveWord.level == level)
    q = q.order_by(SensitiveWord.created_at.desc())
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return {"items": [_fmt(w) for w in items], "total": total}


@router.post("")
def create_word(
    req: SensitiveWordCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_staff),
):
    exist = db.query(SensitiveWord).filter(SensitiveWord.word == req.word).first()
    if exist:
        raise HTTPException(status_code=400, detail="敏感词已存在")
    w = SensitiveWord(word=req.word, level=req.level, remark=req.remark, status=1)
    db.add(w)
    db.commit()
    db.refresh(w)
    return _fmt(w)


@router.put("/{word_id}")
def update_word(
    word_id: int,
    req: SensitiveWordUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_staff),
):
    w = db.query(SensitiveWord).filter(SensitiveWord.id == word_id).first()
    if not w:
        raise HTTPException(status_code=404, detail="敏感词不存在")
    for k, v in req.model_dump(exclude_unset=True).items():
        setattr(w, k, v)
    db.commit()
    db.refresh(w)
    return _fmt(w)


@router.delete("/{word_id}")
def delete_word(
    word_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_staff),
):
    w = db.query(SensitiveWord).filter(SensitiveWord.id == word_id).first()
    if not w:
        raise HTTPException(status_code=404, detail="敏感词不存在")
    db.delete(w)
    db.commit()
    return {"message": "删除成功"}
