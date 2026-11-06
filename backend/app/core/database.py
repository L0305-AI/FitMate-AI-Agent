from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user_profile import Base
from app.models.chat_history import ChatHistory
# 注意：密码
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:你的密码@localhost:3306/fitmate_db?charset=utf8mb4"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,  # 每次从连接池取连接前先 ping 一下，如果断了会自动重连
    pool_recycle=3600    # 每小时强制回收一次连接，防止 MySQL 默认 8 小时断连
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 自动创建表
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()