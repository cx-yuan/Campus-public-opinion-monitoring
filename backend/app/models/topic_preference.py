"""
用户主题订阅模型 - 对应 user_topic_preference 表
"""
from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func

from app.core.database import Base


class TopicPreference(Base):
    __tablename__ = "user_topic_preference"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("sys_user.id", ondelete="CASCADE"), nullable=False)
    category = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=func.now())

    __table_args__ = (UniqueConstraint("user_id", "category", name="uk_user_category"),)
