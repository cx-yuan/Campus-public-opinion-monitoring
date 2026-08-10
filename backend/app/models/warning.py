"""
预警记录模型 - 对应 warning_record 表
"""
from sqlalchemy import Column, BigInteger, String, Integer, DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class Warning(Base):
    __tablename__ = "warning_record"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    opinion_id = Column(BigInteger)
    warning_type = Column(String(50))   # negative_sentiment / sensitive_word / high_frequency
    warning_level = Column(String(20))  # low / medium / high
    warning_message = Column(String(255))
    status = Column(Integer, default=0) # 0 未处理, 1 已处理
    created_at = Column(DateTime, default=func.now())
    handled_at = Column(DateTime, nullable=True)
    handler_id = Column(BigInteger, nullable=True)
