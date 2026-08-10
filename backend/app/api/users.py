"""
用户管理接口：列表、创建、更新、删除
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_password_hash
from app.core.auth_deps import require_admin
from app.models.user import User
from app.models.role import Role
from app.schemas.user import UserCreate, UserUpdate, UserResponse, RoleOption

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.get("/roles", response_model=list[RoleOption])
def list_roles(db: Session = Depends(get_db), _=Depends(require_admin)):
    """获取角色列表（下拉选项）"""
    roles = db.query(Role).all()
    return [RoleOption(id=r.id, role_name=r.role_name, role_code=r.role_code) for r in roles]


@router.get("")
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    keyword: str | None = Query(None, description="用户名或姓名搜索"),
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """用户列表（分页）"""
    q = db.query(User).join(Role)
    if keyword:
        q = q.filter(
            (User.username.contains(keyword)) | (User.real_name.contains(keyword))
        )
    total = q.count()
    offset = (page - 1) * page_size
    users = q.offset(offset).limit(page_size).all()
    items = [
        UserResponse(
            id=u.id,
            username=u.username,
            real_name=u.real_name,
            email=u.email,
            phone=u.phone,
            role_id=u.role_id,
            role_name=u.role.role_name,
            role_code=u.role.role_code,
            status=u.status,
            created_at=u.created_at,
        )
        for u in users
    ]
    return {"items": items, "total": total}


@router.post("", response_model=UserResponse)
def create_user(
    req: UserCreate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """创建用户（仅管理员）"""
    exist = db.query(User).filter(User.username == req.username).first()
    if exist:
        raise HTTPException(status_code=400, detail="用户名已存在")
    role = db.query(Role).filter(Role.id == req.role_id).first()
    if not role:
        raise HTTPException(status_code=400, detail="角色不存在")
    user = User(
        username=req.username,
        password_hash=get_password_hash(req.password),
        real_name=req.real_name,
        email=req.email,
        phone=req.phone,
        role_id=req.role_id,
        status=req.status,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserResponse(
        id=user.id,
        username=user.username,
        real_name=user.real_name,
        email=user.email,
        phone=user.phone,
        role_id=user.role_id,
        role_name=user.role.role_name,
        role_code=user.role.role_code,
        status=user.status,
        created_at=user.created_at,
    )


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """获取用户详情"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return UserResponse(
        id=user.id,
        username=user.username,
        real_name=user.real_name,
        email=user.email,
        phone=user.phone,
        role_id=user.role_id,
        role_name=user.role.role_name,
        role_code=user.role.role_code,
        status=user.status,
        created_at=user.created_at,
    )


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    req: UserUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """更新用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if req.real_name is not None:
        user.real_name = req.real_name
    if req.email is not None:
        user.email = req.email
    if req.phone is not None:
        user.phone = req.phone
    if req.role_id is not None:
        role = db.query(Role).filter(Role.id == req.role_id).first()
        if not role:
            raise HTTPException(status_code=400, detail="角色不存在")
        user.role_id = req.role_id
    if req.status is not None:
        user.status = req.status
    if req.password:
        user.password_hash = get_password_hash(req.password)
    db.commit()
    db.refresh(user)
    return UserResponse(
        id=user.id,
        username=user.username,
        real_name=user.real_name,
        email=user.email,
        phone=user.phone,
        role_id=user.role_id,
        role_name=user.role.role_name,
        role_code=user.role.role_code,
        status=user.status,
        created_at=user.created_at,
    )


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """删除用户"""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能删除自己")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    db.delete(user)
    db.commit()
    return {"message": "删除成功"}
