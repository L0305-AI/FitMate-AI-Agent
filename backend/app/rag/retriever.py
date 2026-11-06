import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from langchain_openai import OpenAIEmbeddings

# 加载 .env 环境变量
load_dotenv()

def get_retriever_results(query: str):
    """
    根据用户查询，从 Qdrant 中检索相关的知识片段
    """
    # 1. 从环境变量读取配置
    qdrant_host = os.getenv("QDRANT_HOST", "localhost")
    qdrant_port = int(os.getenv("QDRANT_PORT", 6333))
    collection_name = os.getenv("QDRANT_COLLECTION", "fitmate_knowledge")
    
    # 2. 初始化 Qdrant 客户端
    client = QdrantClient(host=qdrant_host, port=qdrant_port)
    
    # 3. 初始化 Embedding 模型
    embeddings_model = OpenAIEmbeddings(
        model=os.getenv("EMBEDDING_MODEL", "text-embedding-v2"),
        api_key=os.getenv("EMBEDDING_API_KEY"),
        base_url=os.getenv("EMBEDDING_BASE_URL"),
        check_embedding_ctx_length=False, 
    )
    
    # 4. 将查询词向量化
    query_vector = embeddings_model.embed_query(query)
    
    # 5. 在 Qdrant 中搜索 (使用新版 query_points API)
    response = client.query_points(
        collection_name=collection_name,
        query=query_vector,
        limit=int(os.getenv("RAG_TOP_K", 5)),
        score_threshold=float(os.getenv("RAG_SCORE_THRESHOLD", 0.45))
    )
    
    # 6. 提取结果文本
    search_result = response.points  # 新版返回的结果在 .points 里
    retrieved_texts = []
    for res in search_result:
        retrieved_texts.append(res.payload.get("text", ""))
        
    return retrieved_texts, search_result

if __name__ == "__main__":
    # 测试用例：检验刚才的数据是否成功入库，以及能否被检索出来
    test_queries = [
        "我最近腰疼，还能做硬拉吗？",
        "减脂期蛋白质应该吃多少？",
        "对花生过敏不能吃什么？"
    ]
    
    for query in test_queries:
        print(f"\n🔍 正在检索问题: 【{query}】")
        print("-" * 50)
        texts, raw_results = get_retriever_results(query)
        
        if not texts:
            print("⚠️ 没有检索到相关内容 (可能是得分低于0.45的阈值)。")
        else:
            for i, res in enumerate(raw_results):
                print(f"[结果 {i+1}] 得分: {res.score:.4f}")
                # 打印前100个字符，方便控制台查看
                content_preview = res.payload.get('text', '').replace('\n', ' ')[:100]
                print(f"内容: {content_preview}...")
        print("-" * 50)