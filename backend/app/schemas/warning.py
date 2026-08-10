"""
预警相关 Pydantic 模型
"""
from datetime import datetime
from pydantic import BaseModel


class WarningResponse(BaseModel):
    id: int
    opinion_id: int | None
    warning_type: str | None
    warning_level: str | None
    warning_message: str | None
    status: int
    created_at: datetime | None
    handled_at: datetime | None
    handler_id: int | None

    class Config:
        from_attributes = True
