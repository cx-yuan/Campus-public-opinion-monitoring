"""
用户收藏接口：添加、移除、列表
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth_deps import get_current_user
from app.models.favorite import Favorite
from app.models.opinion import Opinion
from app.models.user import User
from app.schemas.opinion import OpinionResponse

router = APIRouter(prefix="/favorites", tags=["收藏"])


def _to_response(o: Opinion):
    score = o.sentiment_score
    risk_score = o.risk_score
    return OpinionResponse(
        id=o.id,
        title=o.title,
        content=o.content,
        source_platform=o.source_platform,
        source_url=o.source_url,
        author=o.author,
        publish_time=o.publish_time,
        keywords=o.keywords,
        sentiment=o.sentiment,
        sentiment_score=float(score) if score is not None else None,
        category=o.category,
        is_warning=o.is_warning or 0,
        content_hash=o.content_hash,
        crawl_time=o.crawl_time,
        created_at=o.created_at,
        risk_level=o.risk_level,
        risk_score=float(risk_score) if risk_score is not None else None,
        risk_detail=o.risk_detail,
    )


@router.get("")
def list_favorites(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """我的收藏列表"""
    q = (
        db.query(Opinion)
        .join(Favorite, Favorite.opinion_id == Opinion.id)
        .filter(Favorite.user_id == current_user.id)
        .order_by(Favorite.created_at.desc())
    )
    total = q.count()
    offset = (page - 1) * page_size
    items = q.offset(offset).limit(page_size).all()
    return {"items": [_to_response(o) for o in items], "total": total}


@router.post("/{opinion_id}")
def add_favorite(
    opinion_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """收藏舆情"""
    opinion = db.query(Opinion).filter(Opinion.id == opinion_id).first()
    if not opinion:
        raise HTTPException(status_code=404, detail="舆情不存在")
    exist = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.opinion_id == opinion_id,
    ).first()
    if exist:
        return {"message": "已收藏"}
    fav = Favorite(user_id=current_user.id, opinion_id=opinion_id)
    db.add(fav)
    db.commit()
    return {"message": "收藏成功"}


@router.delete("/{opinion_id}")
def remove_favorite(
    opinion_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """取消收藏"""
    fav = db.query(Favorite).filter(
        Favorite.user_id == current_user.id,
        Favorite.opinion_id == opinion_id,
    ).first()
    if fav:
        db.delete(fav)
        db.commit()
    return {"message": "已取消收藏"}


@router.get("/ids")
def get_favorite_ids(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取当前用户已收藏的舆情 ID 列表（用于前端标记）"""
    rows = db.query(Favorite.opinion_id).filter(Favorite.user_id == current_user.id).all()
    return {"ids": [r[0] for r in rows]}
