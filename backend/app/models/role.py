"""
角色模型 - 对应 sys_role 表
"""
from sqlalchemy import Column, BigInteger, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Role(Base):
    __tablename__ = "sys_role"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    role_name = Column(String(50), nullable=False, unique=True)
    role_code = Column(String(50), nullable=False, unique=True)
    description = Column(String(255))
    created_at = Column(DateTime, default=func.now())

    users = relationship("User", back_populates="role")
