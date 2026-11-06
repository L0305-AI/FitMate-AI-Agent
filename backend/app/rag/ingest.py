import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "fitmate_knowledge"
CHUNK_SIZE = 600      # 调大了，保证上下文完整
CHUNK_OVERLAP = 100

def ingest_data():
    print("🚀 开始执行知识库灌入流程...")
    
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    
    # 如果集合已存在，先删除
    if client.collection_exists(collection_name=COLLECTION_NAME):
        print(f"检测到旧集合 {COLLECTION_NAME}，正在删除...")
        client.delete_collection(collection_name=COLLECTION_NAME)
        
    print(f"创建新集合: {COLLECTION_NAME}")
    client.create_collection(
        collection_name=COLLECTION_NAME,
       vectors_config=VectorParams(size=int(os.getenv("EMBEDDING_DIM", 1024)), distance=Distance.COSINE), # text-embedding-3-small 是 1536 维
    )

    # 读取数据
    data_dir = os.path.join(os.path.dirname(__file__), "../../data/")
    files = ["fitness_guide.txt", "nutrition_guide.txt"]
    
    all_documents = []
    for file_name in files:
        file_path = os.path.join(data_dir, file_name)
        if os.path.exists(file_path):
            loader = TextLoader(file_path, encoding='utf-8')
            all_documents.extend(loader.load())
            print(f"✅ 已读取: {file_name}")
        else:
            print(f"⚠️ 找不到文件: {file_path}")

    # 文本切片
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
    )
    chunks = text_splitter.split_documents(all_documents)
    print(f"切分完成，共得到 {len(chunks)} 个文本块。")

    # 向量化
    print("正在调用 Embedding 模型进行向量化...")
    # 如果你用的是通义千问，请改成: from langchain_community.embeddings import DashScopeEmbeddings
    # embeddings_model = DashScopeEmbeddings(model="text-embedding-v2")
    embeddings_model = OpenAIEmbeddings(
    model=os.getenv("EMBEDDING_MODEL", "qwen3.7-text-embedding-flash"),
    api_key=os.getenv("EMBEDDING_API_KEY"),
    base_url=os.getenv("EMBEDDING_BASE_URL"),
    check_embedding_ctx_length=False, 
    # 阿里千问的 embedding 接口一次最多接受 25 条文本，设置批次
    chunk_size=int(os.getenv("EMBEDDING_BATCH_SIZE", 20)) 
    )
    
    texts = [chunk.page_content for chunk in chunks]
    vectors = embeddings_model.embed_documents(texts)

    # 构造 Qdrant 数据
    points = []
    for i, (text, vector) in enumerate(zip(texts, vectors)):
        points.append({
            "id": i, 
            "vector": vector,
            "payload": {"text": text}
        })

    print("正在将向量写入 Qdrant...")
    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print("🎉 知识库灌入完成！")

if __name__ == "__main__":
    ingest_data()