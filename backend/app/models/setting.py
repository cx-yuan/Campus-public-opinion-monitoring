"""系统配置模型 - 对应 sys_setting 表"""
from sqlalchemy import Column, BigInteger, String, DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class SysSetting(Base):
    __tablename__ = "sys_setting"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    setting_key = Column(String(100), nullable=False, unique=True)
    setting_value = Column(String(255))
    setting_name = Column(String(100))
    remark = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
