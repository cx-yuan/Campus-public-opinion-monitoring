"""系统配置管理接口"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth_deps import require_staff
from app.models.setting import SysSetting
from app.models.user import User

router = APIRouter(prefix="/settings", tags=["系统配置"])


class SettingUpdate(BaseModel):
    setting_value: str


@router.get("")
def list_settings(
    db: Session = Depends(get_db),
    _: User = Depends(require_staff),
):
    """获取所有系统配置（key-value 列表）"""
    items = db.query(SysSetting).order_by(SysSetting.id).all()
    return {
        "items": [
            {
                "id": s.id,
                "setting_key": s.setting_key,
                "setting_value": s.setting_value,
                "setting_name": s.setting_name,
                "remark": s.remark,
            }
            for s in items
        ]
    }


@router.get("/{key}")
def get_setting(
    key: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_staff),
):
    """根据 key 获取单个配置"""
    s = db.query(SysSetting).filter(SysSetting.setting_key == key).first()
    if not s:
        return {"setting_key": key, "setting_value": None}
    return {"setting_key": s.setting_key, "setting_value": s.setting_value}


@router.put("/{key}")
def update_setting(
    key: str,
    req: SettingUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_staff),
):
    """更新配置项"""
    s = db.query(SysSetting).filter(SysSetting.setting_key == key).first()
    if not s:
        return {"message": "配置项不存在"}
    s.setting_value = req.setting_value
    db.commit()
    return {"message": "更新成功", "setting_key": key, "setting_value": req.setting_value}
