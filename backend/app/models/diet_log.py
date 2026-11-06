from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.models.user_profile import Base

class DietLog(Base):
    __tablename__ = "diet_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), index=True)
    food_name = Column(String(100))
    calories = Column(Integer)
    meal_type = Column(String(20)) # 早餐、午餐、晚餐、加餐
    recorded_at = Column(DateTime, default=datetime.now)