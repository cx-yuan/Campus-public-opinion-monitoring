"""
舆情相关 Pydantic 模型
"""
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel


class OpinionBase(BaseModel):
    """舆情基础字段"""
    title: str | None = None
    content: str | None = None
    source_platform: str | None = None
    source_url: str | None = None
    author: str | None = None
    publish_time: datetime | None = None
    keywords: str | None = None
    sentiment: str | None = None  # positive/neutral/negative
    sentiment_score: float | None = None
    category: str | None = None  # 教学、宿舍、食堂、安全、后勤
    is_warning: int = 0


class OpinionCreate(OpinionBase):
    """创建舆情"""
    pass


class OpinionUpdate(BaseModel):
    """更新舆情"""
    title: str | None = None
    content: str | None = None
    source_platform: str | None = None
    source_url: str | None = None
    author: str | None = None
    publish_time: datetime | None = None
    keywords: str | None = None
    sentiment: str | None = None
    sentiment_score: float | None = None
    category: str | None = None
    is_warning: int | None = None


class OpinionResponse(OpinionBase):
    """舆情响应"""
    id: int
    content_hash: str | None = None
    crawl_time: datetime | None = None
    created_at: datetime | None = None
    risk_level: str | None = None
    risk_score: float | None = None
    risk_detail: str | None = None

    class Config:
        from_attributes = True
