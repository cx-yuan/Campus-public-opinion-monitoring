"""
用户主题订阅接口
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.database import get_db
from app.core.auth_deps import get_current_user
from app.models.topic_preference import TopicPreference
from app.models.user import User
from sqlalchemy.orm import Session

router = APIRouter(prefix="/topic-preferences", tags=["主题订阅"])

# 系统支持的分类（与舆情 category 对应）
ALL_CATEGORIES = ["教学", "宿舍", "食堂", "安全", "后勤", "图书馆", "其他"]


@router.get("/options")
def get_category_options():
    """获取可订阅的主题选项"""
    return {"categories": ALL_CATEGORIES}


class TopicListRequest(BaseModel):
    categories: list[str]


@router.get("")
def get_my_topics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取当前用户订阅的主题"""
    rows = db.query(TopicPreference.category).filter(TopicPreference.user_id == current_user.id).all()
    return {"categories": [r[0] for r in rows]}


@router.put("", response_model=dict)
def update_my_topics(
    req: TopicListRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新订阅的主题（覆盖）"""
    # 删除原有
    db.query(TopicPreference).filter(TopicPreference.user_id == current_user.id).delete()
    # 添加新选
    for cat in req.categories:
        if cat and isinstance(cat, str) and cat.strip():
            db.add(TopicPreference(user_id=current_user.id, category=cat.strip()))
    db.commit()
    return {"message": "更新成功", "categories": req.categories}
