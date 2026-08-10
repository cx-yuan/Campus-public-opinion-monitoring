"""
用户模型 - 对应 sys_user 表
"""
from sqlalchemy import Column, BigInteger, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class User(Base):
    __tablename__ = "sys_user"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    real_name = Column(String(50))
    email = Column(String(100))
    phone = Column(String(20))
    avatar = Column(String(255))
    role_id = Column(BigInteger, ForeignKey("sys_role.id"), nullable=False)
    status = Column(Integer, default=1)  # 1 正常，0 禁用
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    role = relationship("Role", back_populates="users")
