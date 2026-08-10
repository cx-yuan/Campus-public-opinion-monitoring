"""
首页看板统计接口
"""
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.auth_deps import get_current_user
from app.models.opinion import Opinion
from app.models.warning import Warning
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["看板统计"])


@router.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """顶部统计卡片数据"""
    try:
        total = db.query(func.count(Opinion.id)).scalar() or 0
        today = datetime.now().date()
        today_count = (
            db.query(func.count(Opinion.id))
            .filter(func.date(Opinion.created_at) == today)
            .scalar() or 0
        )
        pending_warning = (
            db.query(func.count(Warning.id))
            .filter(Warning.status == 0)
            .scalar() or 0
        )
        platform_count = (
            db.query(func.count(func.distinct(Opinion.source_platform)))
            .scalar() or 0
        )
        return {
            "total": total,
            "today": today_count,
            "pending_warning": pending_warning,
            "platform_count": platform_count,
        }
    except Exception:
        return {"total": 0, "today": 0, "pending_warning": 0, "platform_count": 0}


@router.get("/sentiment")
def get_sentiment(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """情感分布（饼图）"""
    try:
        rows = (
            db.query(Opinion.sentiment, func.count(Opinion.id).label("cnt"))
            .group_by(Opinion.sentiment)
            .all()
        )
        label_map = {"positive": "正向", "neutral": "中性", "negative": "负向"}
        data = [
            {"name": label_map.get(r.sentiment or "neutral", r.sentiment or "未知"), "value": r.cnt}
            for r in rows
        ]
        return {"data": data}
    except Exception:
        return {"data": []}


@router.get("/platform")
def get_platform(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """来源平台分布（饼图）"""
    try:
        rows = (
            db.query(Opinion.source_platform, func.count(Opinion.id).label("cnt"))
            .filter(Opinion.source_platform.isnot(None))
            .group_by(Opinion.source_platform)
            .order_by(func.count(Opinion.id).desc())
            .limit(8)
            .all()
        )
        data = [{"name": r.source_platform or "未知", "value": r.cnt} for r in rows]
        return {"data": data}
    except Exception:
        return {"data": []}


@router.get("/risk")
def get_risk(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """贝叶斯风险等级分布（饼图）"""
    try:
        rows = (
            db.query(Opinion.risk_level, func.count(Opinion.id).label("cnt"))
            .filter(Opinion.risk_level.isnot(None))
            .group_by(Opinion.risk_level)
            .all()
        )
        label_map = {"low": "低风险", "medium": "中风险", "high": "高风险"}
        data = [
            {"name": label_map.get(r.risk_level, r.risk_level or "未知"), "value": r.cnt}
            for r in rows
        ]
        return {"data": data}
    except Exception:
        return {"data": []}


@router.get("/hot")
def get_hot_opinions(
    period: str = "week",
    limit: int = 8,
    categories: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """热门舆情：近期数据按创建时间排序"""
    try:
        today = datetime.now().date()
        days = 30 if period == "month" else 7
        start = today - timedelta(days=days)
        q = db.query(Opinion).filter(func.date(Opinion.created_at) >= start)
        if categories:
            cats = [c.strip() for c in categories.split(",") if c.strip()]
            if cats:
                q = q.filter(Opinion.category.in_(cats))
        q = q.order_by(Opinion.created_at.desc()).limit(limit)
        items = q.all()

        def _to_res(o):
            return {
                "id": o.id,
                "title": o.title,
                "content": (o.content or "")[:80],
                "source_platform": o.source_platform,
                "sentiment": o.sentiment,
                "category": o.category,
                "publish_time": o.publish_time.isoformat() if o.publish_time else None,
                "created_at": o.created_at.isoformat() if o.created_at else None,
            }
        return {"data": [_to_res(o) for o in items]}
    except Exception:
        return {"data": []}


@router.get("/trend")
def get_trend(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """近 7 天舆情趋势（折线图）"""
    try:
        today = datetime.now().date()
        result = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            cnt = (
                db.query(func.count(Opinion.id))
                .filter(func.date(Opinion.created_at) == day)
                .scalar() or 0
            )
            result.append({"date": day.strftime("%m/%d"), "count": cnt})
        return {"data": result}
    except Exception:
        return {"data": []}
