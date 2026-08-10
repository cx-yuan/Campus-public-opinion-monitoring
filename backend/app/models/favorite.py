"""
用户收藏模型 - 对应 user_favorite 表
"""
from sqlalchemy import Column, BigInteger, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func

from app.core.database import Base


class Favorite(Base):
    __tablename__ = "user_favorite"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("sys_user.id", ondelete="CASCADE"), nullable=False)
    opinion_id = Column(BigInteger, ForeignKey("opinion_data.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=func.now())

    __table_args__ = (UniqueConstraint("user_id", "opinion_id", name="uk_user_opinion"),)
