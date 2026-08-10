"""
敏感词模型 - 对应 sensitive_word 表
"""
from sqlalchemy import Column, BigInteger, String, SmallInteger, DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class SensitiveWord(Base):
    __tablename__ = "sensitive_word"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    word = Column(String(100), nullable=False, unique=True)
    level = Column(String(20), default="high")   # high / medium / low
    status = Column(SmallInteger, default=1)      # 1启用 0禁用
    remark = Column(String(255))
    created_at = Column(DateTime, default=func.now())
