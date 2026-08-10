"""
采集任务管理接口
"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth_deps import require_staff
from app.models.task import CrawlTask
from app.models.user import User

router = APIRouter(prefix="/tasks", tags=["采集任务"])


class TaskCreate(BaseModel):
    task_name: str
    platform: str = "百度新闻"
    cron_expr: str = "0 */1 * * *"
    keyword_ids: str = ""


class TaskUpdate(BaseModel):
    task_name: str | None = None
    platform: str | None = None
    cron_expr: str | None = None
    keyword_ids: str | None = None
    status: int | None = None


def _fmt(t: CrawlTask) -> dict:
    return {
        "id": t.id,
        "task_name": t.task_name,
        "platform": t.platform,
        "cron_expr": t.cron_expr,
        "keyword_ids": t.keyword_ids,
        "status": t.status,
        "last_run_time": t.last_run_time,
        "created_at": t.created_at,
    }


@router.get("")
def list_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_staff),
):
    q = db.query(CrawlTask).order_by(CrawlTask.created_at.desc())
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return {"items": [_fmt(t) for t in items], "total": total}


@router.post("")
def create_task(
    req: TaskCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_staff),
):
    t = CrawlTask(
        task_name=req.task_name,
        platform=req.platform,
        cron_expr=req.cron_expr,
        keyword_ids=req.keyword_ids,
        status=1,
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return _fmt(t)


@router.put("/{task_id}")
def update_task(
    task_id: int,
    req: TaskUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_staff),
):
    t = db.query(CrawlTask).filter(CrawlTask.id == task_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="任务不存在")
    for k, v in req.model_dump(exclude_unset=True).items():
        setattr(t, k, v)
    db.commit()
    db.refresh(t)
    return _fmt(t)


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_staff),
):
    t = db.query(CrawlTask).filter(CrawlTask.id == task_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="任务不存在")
    db.delete(t)
    db.commit()
    return {"message": "删除成功"}


@router.post("/{task_id}/run")
def run_task(
    task_id: int,
    background_tasks: BackgroundTasks,
    sync: bool = False,
    db: Session = Depends(get_db),
    _: User = Depends(require_staff),
):
    """手动触发采集任务。sync=1 时同步执行并返回采集条数，否则后台执行"""
    t = db.query(CrawlTask).filter(CrawlTask.id == task_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="任务不存在")

    if sync:
        from app.services.crawler import run_crawl_task
        result = run_crawl_task(task_id, db)
        return {
            "message": f"采集完成，新增 {result['added']} 条舆情",
            "added": result["added"],
            "keywords": result.get("keywords", []),
        }

    def _run():
        from app.core.database import SessionLocal
        from app.services.crawler import run_crawl_task
        _db = SessionLocal()
        try:
            run_crawl_task(task_id, _db)
        finally:
            _db.close()

    background_tasks.add_task(_run)
    return {"message": "采集任务已启动，正在后台执行，请 1-2 分钟后在舆情列表中查看结果"}


@router.post("/quick-crawl")
def quick_crawl(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _: User = Depends(require_staff),
):
    """快速采集：使用所有启用关键词立即爬取，无需配置任务"""
    def _run():
        from app.core.database import SessionLocal
        from app.models.keyword import Keyword
        from app.services.crawler import crawl_by_keyword
        import time, random
        _db = SessionLocal()
        try:
            kws = _db.query(Keyword).filter(Keyword.status == 1).all()
            for kw in kws:
                crawl_by_keyword(kw.keyword, _db)
                time.sleep(random.uniform(1.0, 2.5))
        finally:
            _db.close()

    background_tasks.add_task(_run)
    return {"message": "快速采集已启动，正在后台执行，请 1-2 分钟后在舆情列表中查看结果"}
