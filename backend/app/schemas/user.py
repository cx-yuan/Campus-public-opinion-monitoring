"""
用户相关 Pydantic 模型
"""
from datetime import datetime
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    """用户基础信息"""
    username: str
    real_name: str | None = None
    email: str | None = None
    phone: str | None = None
    role_id: int
    status: int = 1


class UserCreate(UserBase):
    """创建用户请求"""
    password: str = Field(min_length=6)


class UserUpdate(BaseModel):
    """更新用户请求"""
    real_name: str | None = None
    email: str | None = None
    phone: str | None = None
    role_id: int | None = None
    status: int | None = None
    password: str | None = Field(default=None, min_length=6)


class UserResponse(BaseModel):
    """用户列表/详情响应"""
    id: int
    username: str
    real_name: str | None
    email: str | None
    phone: str | None
    role_id: int
    role_name: str | None = None
    role_code: str | None = None
    status: int
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class RoleOption(BaseModel):
    """角色选项（下拉用）"""
    id: int
    role_name: str
    role_code: str

    class Config:
        from_attributes = True
