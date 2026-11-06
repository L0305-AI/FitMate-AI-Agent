from sqlalchemy import Column, Integer, String
from app.models.user_profile import Base

class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), index=True)
    calories = Column(Integer)
    description = Column(String(200))