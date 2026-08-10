"""
采集任务模型 - 对应 crawl_task 表
"""
from sqlalchemy import Column, BigInteger, String, SmallInteger, DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class CrawlTask(Base):
    __tablename__ = "crawl_task"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    task_name = Column(String(100), nullable=False)
    platform = Column(String(50))
    cron_expr = Column(String(50), nullable=False, default="0 */1 * * *")
    keyword_ids = Column(String(255))       # 逗号分隔的关键词ID
    status = Column(SmallInteger, default=1) # 1启用 0禁用
    last_run_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
