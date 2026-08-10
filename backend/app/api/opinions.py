"""
舆情数据接口：增删改查、筛选、情感分析
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.core.auth_deps import get_current_user, require_staff
from app.models.opinion import Opinion
from app.models.user import User
from app.schemas.opinion import OpinionCreate, OpinionUpdate, OpinionResponse
from app.services.cleaner import clean_text, compute_hash
from app.services.sentiment import analyze_sentiment
from app.services.classifier import classify_category
from app.services.warning_service import check_and_warn
from app.services.bayes import assess as bayes_assess

router = APIRouter(prefix="/opinions", tags=["舆情管理"])


def _to_response(o: Opinion) -> dict:
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
def list_opinions(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    keyword: str | None = Query(None, description="关键词搜索 title/content/keywords"),
    sentiment: str | None = Query(None, description="情感筛选 positive/neutral/negative"),
    source_platform: str | None = Query(None, description="来源平台筛选"),
    category: str | None = Query(None, description="主题分类筛选"),
    categories: str | None = Query(None, description="多主题筛选，逗号分隔，如 食堂,宿舍"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """舆情列表（分页、筛选）"""
    q = db.query(Opinion)
    if keyword:
        q = q.filter(
            or_(
                Opinion.title.contains(keyword),
                Opinion.content.contains(keyword),
                Opinion.keywords.contains(keyword),
            )
        )
    if sentiment:
        q = q.filter(Opinion.sentiment == sentiment)
    if source_platform:
        q = q.filter(Opinion.source_platform.contains(source_platform))
    if categories:
        cats = [c.strip() for c in categories.split(",") if c.strip()]
        if cats:
            q = q.filter(Opinion.category.in_(cats))
    elif category:
        q = q.filter(Opinion.category == category)

    q = q.order_by(Opinion.created_at.desc())
    total = q.count()
    offset = (page - 1) * page_size
    items = q.offset(offset).limit(page_size).all()
    return {"items": [_to_response(o) for o in items], "total": total}


@router.post("", response_model=OpinionResponse)
def create_opinion(
    req: OpinionCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_staff),
):
    """创建舆情（手动添加）"""
    o = Opinion(
        title=req.title,
        content=req.content,
        source_platform=req.source_platform,
        source_url=req.source_url,
        author=req.author,
        publish_time=req.publish_time,
        keywords=req.keywords,
        sentiment=req.sentiment,
        sentiment_score=req.sentiment_score,
        category=req.category,
        is_warning=req.is_warning or 0,
    )
    db.add(o)
    db.commit()
    db.refresh(o)
    return _to_response(o)


@router.get("/{opinion_id}", response_model=OpinionResponse)
def get_opinion(
    opinion_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """获取舆情详情"""
    o = db.query(Opinion).filter(Opinion.id == opinion_id).first()
    if not o:
        raise HTTPException(status_code=404, detail="舆情不存在")
    return _to_response(o)


@router.put("/{opinion_id}", response_model=OpinionResponse)
def update_opinion(
    opinion_id: int,
    req: OpinionUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_staff),
):
    """更新舆情"""
    o = db.query(Opinion).filter(Opinion.id == opinion_id).first()
    if not o:
        raise HTTPException(status_code=404, detail="舆情不存在")
    for k, v in req.model_dump(exclude_unset=True).items():
        setattr(o, k, v)
    db.commit()
    db.refresh(o)
    return _to_response(o)


@router.delete("/{opinion_id}")
def delete_opinion(
    opinion_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_staff),
):
    """删除舆情"""
    o = db.query(Opinion).filter(Opinion.id == opinion_id).first()
    if not o:
        raise HTTPException(status_code=404, detail="舆情不存在")
    db.delete(o)
    db.commit()
    return {"message": "删除成功"}


@router.post("/batch-analyze")
def batch_analyze(
    db: Session = Depends(get_db),
    _: User = Depends(require_staff),
):
    """批量分析所有未标注情感的舆情"""
    items = db.query(Opinion).filter(
        (Opinion.sentiment == None) | (Opinion.sentiment == "")  # noqa: E711
    ).all()

    count = 0
    for o in items:
        raw_text = (o.content or o.title or "")
        cleaned = clean_text(raw_text)
        sentiment, score = analyze_sentiment(cleaned or o.title or "")
        category = classify_category(title=o.title or "", content=cleaned)
        o.sentiment = sentiment
        o.sentiment_score = score
        o.category = category
        if cleaned and not o.content_hash:
            o.content_hash = compute_hash(cleaned)
        count += 1

    db.commit()

    # 批量分析后逐条执行预警检测
    for o in items:
        check_and_warn(o, db)

    return {"message": f"已分析 {count} 条舆情"}


@router.post("/{opinion_id}/analyze", response_model=OpinionResponse)
def analyze_opinion(
    opinion_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_staff),
):
    """对单条舆情执行情感分析 + 主题分类 + 文本清洗"""
    o = db.query(Opinion).filter(Opinion.id == opinion_id).first()
    if not o:
        raise HTTPException(status_code=404, detail="舆情不存在")

    raw_text = (o.content or o.title or "")
    cleaned = clean_text(raw_text)

    sentiment, score = analyze_sentiment(cleaned or o.title or "")
    category = classify_category(title=o.title or "", content=cleaned)

    o.sentiment = sentiment
    o.sentiment_score = score
    o.category = category
    if cleaned and not o.content_hash:
        o.content_hash = compute_hash(cleaned)

    db.commit()
    db.refresh(o)

    # 分析完毕后自动执行预警检测
    check_and_warn(o, db)

    return _to_response(o)


@router.post("/batch-risk")
def batch_risk(
    db: Session = Depends(get_db),
    _: User = Depends(require_staff),
):
    """批量贝叶斯风险评估（对所有已分析情感、未评估风险的舆情执行）"""
    from datetime import datetime, timedelta
    from sqlalchemy import func as sqlfunc
    import json

    items = db.query(Opinion).filter(
        Opinion.sentiment.isnot(None),
        (Opinion.risk_level == None) | (Opinion.risk_level == ""),  # noqa: E711
    ).all()

    count = 0
    for o in items:
        # 计算近24h同关键词发文数
        recent_count = 1
        if o.keywords:
            kw_list = [k.strip() for k in o.keywords.split(",") if k.strip()]
            if kw_list:
                cutoff = datetime.now() - timedelta(hours=24)
                recent_count = db.query(sqlfunc.count(Opinion.id)).filter(
                    Opinion.keywords.contains(kw_list[0]),
                    Opinion.created_at >= cutoff,
                ).scalar() or 1

        result = bayes_assess(
            sentiment=o.sentiment,
            sensitive_hit=bool(o.is_warning),
            platform=o.source_platform,
            recent_count=recent_count,
        )
        o.risk_level = result.risk_level
        o.risk_score = result.risk_score
        o.risk_detail = json.dumps(result.detail, ensure_ascii=False)
        count += 1

    db.commit()
    return {"message": f"已完成 {count} 条舆情的风险评估"}


@router.post("/{opinion_id}/risk", response_model=OpinionResponse)
def assess_risk(
    opinion_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_staff),
):
    """对单条舆情执行贝叶斯风险评估"""
    from datetime import datetime, timedelta
    from sqlalchemy import func as sqlfunc
    import json

    o = db.query(Opinion).filter(Opinion.id == opinion_id).first()
    if not o:
        raise HTTPException(status_code=404, detail="舆情不存在")

    recent_count = 1
    if o.keywords:
        kw_list = [k.strip() for k in o.keywords.split(",") if k.strip()]
        if kw_list:
            cutoff = datetime.now() - timedelta(hours=24)
            recent_count = db.query(sqlfunc.count(Opinion.id)).filter(
                Opinion.keywords.contains(kw_list[0]),
                Opinion.created_at >= cutoff,
            ).scalar() or 1

    result = bayes_assess(
        sentiment=o.sentiment,
        sensitive_hit=bool(o.is_warning),
        platform=o.source_platform,
        recent_count=recent_count,
    )
    o.risk_level = result.risk_level
    o.risk_score = result.risk_score
    o.risk_detail = json.dumps(result.detail, ensure_ascii=False)

    db.commit()
    db.refresh(o)
    return _to_response(o)
