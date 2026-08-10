"""
认证接口：注册、登录、当前用户
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.auth_deps import get_current_user
from app.models.user import User
from app.models.role import Role
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, ChangePasswordRequest
from app.schemas.user import UserResponse

router = APIRouter(prefix="/auth", tags=["认证"])


@router.get("/register-roles")
def get_register_roles(db: Session = Depends(get_db)):
    """获取可注册的角色（不含管理员）"""
    roles = db.query(Role).filter(Role.role_code != "admin").all()
    return [{"id": r.id, "role_name": r.role_name, "role_code": r.role_code} for r in roles]


@router.post("/register", response_model=dict)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """用户注册"""
    if not req.username or not req.password:
        raise HTTPException(status_code=400, detail="用户名和密码不能为空")

    # 检查用户名是否已存在
    exist = db.query(User).filter(User.username == req.username).first()
    if exist:
        raise HTTPException(status_code=400, detail="用户名已存在")

    # 确定角色：禁止注册为管理员
    if req.role_id:
        role = db.query(Role).filter(Role.id == req.role_id).first()
        if not role:
            raise HTTPException(status_code=400, detail="所选角色不存在")
        if role.role_code == "admin":
            raise HTTPException(status_code=400, detail="禁止注册为管理员")
    else:
        role = db.query(Role).filter(Role.role_code == "user").first()
    if not role:
        raise HTTPException(status_code=500, detail="系统角色未初始化，请先执行 SQL 初始化")

    user = User(
        username=req.username,
        password_hash=req.password,  # 明文存储，不加密
        role_id=role.id,
        status=1,
        email=req.email or None,
        phone=req.phone or None,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "注册成功", "user_id": user.id}


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """用户登录"""
    if not req.username or not req.password:
        raise HTTPException(status_code=400, detail="用户名和密码不能为空")

    user = db.query(User).filter(User.username == req.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    if user.status != 1:
        raise HTTPException(status_code=401, detail="账号已被禁用")

    if not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = create_access_token(data={"sub": str(user.id), "username": user.username})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        username=user.username,
        role_code=user.role.role_code,
    )


@router.post("/change-password")
def change_password(
    req: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """修改当前用户密码"""
    if not req.old_password or not req.new_password:
        raise HTTPException(status_code=400, detail="原密码和新密码不能为空")
    if len(req.new_password) < 6:
        raise HTTPException(status_code=400, detail="新密码至少6位")
    if not verify_password(req.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="原密码错误")
    current_user.password_hash = get_password_hash(req.new_password)
    db.commit()
    return {"message": "密码修改成功"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息（仅返回本人，不暴露其他用户）"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        real_name=current_user.real_name,
        email=current_user.email,
        phone=current_user.phone,
        role_id=current_user.role_id,
        role_name=current_user.role.role_name if current_user.role else None,
        role_code=current_user.role.role_code if current_user.role else None,
        status=current_user.status,
        created_at=current_user.created_at,
    )
