import os
from dotenv import load_dotenv

# 加载 .env
load_dotenv()

class Settings:
    # LLM 配置
    LLM_API_KEY = os.getenv("LLM_API_KEY")
    LLM_BASE_URL = os.getenv("LLM_BASE_URL")
    LLM_MODEL = os.getenv("LLM_MODEL", "qwen-plus")
    
    # Embedding 配置
    EMBEDDING_API_KEY = os.getenv("EMBEDDING_API_KEY")
    EMBEDDING_BASE_URL = os.getenv("EMBEDDING_BASE_URL")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-v2")
    EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", 1024))
    
    # Qdrant 配置
    QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
    QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "fitmate_knowledge")
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:123456@localhost:3306/fitmate_db?charset=utf8mb4"

settings = Settings()