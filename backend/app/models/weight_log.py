from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.models.user_profile import Base

class WeightLog(Base):
    __tablename__ = "weight_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), index=True)
    weight_kg = Column(Float)
    recorded_at = Column(DateTime, default=datetime.now)