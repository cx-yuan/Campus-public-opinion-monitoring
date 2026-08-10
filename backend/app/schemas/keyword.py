"""
关键词相关 Pydantic 模型
"""
from datetime import datetime
from pydantic import BaseModel


class KeywordCreate(BaseModel):
    keyword: str
    weight: int = 1
    status: int = 1
    remark: str | None = None


class KeywordUpdate(BaseModel):
    weight: int | None = None
    status: int | None = None
    remark: str | None = None


class KeywordResponse(BaseModel):
    id: int
    keyword: str
    weight: int
    status: int
    remark: str | None
    created_at: datetime | None

    class Config:
        from_attributes = True
