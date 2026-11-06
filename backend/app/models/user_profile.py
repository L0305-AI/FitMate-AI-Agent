from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), unique=True, index=True) # 比如前端的会话ID或用户名
    height_cm = Column(Float, nullable=True)              # 身高
    weight_kg = Column(Float, nullable=True)              # 体重
    gender = Column(String(10), nullable=True)            # 性别
    age = Column(Integer, nullable=True)                  # 年龄
    allergy = Column(String(100), nullable=True)          # 过敏史
    age = Column(Integer, nullable=True)                  # 年龄
    gender = Column(String(10), nullable=True)            # 性别
    injury = Column(String(100), nullable=True)           # 伤病