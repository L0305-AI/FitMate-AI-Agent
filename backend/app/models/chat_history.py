from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.models.user_profile import Base

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), index=True)
    role = Column(String(20)) # user 或 assistant
    content = Column(Text)    # 聊天内容
    created_at = Column(DateTime, default=datetime.now)