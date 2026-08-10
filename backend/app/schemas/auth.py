"""
认证相关 Pydantic 模型
"""
from pydantic import BaseModel


class RegisterRequest(BaseModel):
    """注册请求"""
    username: str
    password: str
    role_id: int | None = None  # 可选，不传则默认普通用户；禁止传管理员 role
    email: str | None = None
    phone: str | None = None


class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str


class TokenResponse(BaseModel):
    """登录成功返回"""
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    role_code: str


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str
    new_password: str
