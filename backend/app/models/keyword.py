"""
关键词模型 - 对应 monitor_keyword 表
"""
from sqlalchemy import Column, BigInteger, String, Integer, DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class Keyword(Base):
    __tablename__ = "monitor_keyword"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    keyword = Column(String(100), nullable=False, unique=True)
    weight = Column(Integer, default=1)
    status = Column(Integer, default=1)   # 1 启用, 0 禁用
    remark = Column(String(255))
    created_at = Column(DateTime, default=func.now())
