"""
舆情数据模型 - 对应 opinion_data 表
"""
from sqlalchemy import Column, BigInteger, String, Integer, DateTime, Text, Numeric
from sqlalchemy.sql import func

from app.core.database import Base


class Opinion(Base):
    __tablename__ = "opinion_data"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String(255))
    content = Column(Text)
    source_platform = Column(String(50))
    source_url = Column(String(500))
    author = Column(String(100))
    publish_time = Column(DateTime)
    keywords = Column(String(255))
    sentiment = Column(String(20))  # positive/neutral/negative
    sentiment_score = Column(Numeric(5, 2))
    category = Column(String(50))  # 教学、宿舍、食堂、安全、后勤等
    is_warning = Column(Integer, default=0)
    content_hash = Column(String(64))
    crawl_time = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    risk_level = Column(String(20))         # low / medium / high
    risk_score = Column(Numeric(5, 4))      # 0~1 贝叶斯风险概率
    risk_detail = Column(String(500))       # JSON 格式各节点概率明细
