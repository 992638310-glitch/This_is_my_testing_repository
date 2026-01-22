import os

class Config:
    # 基础设施配置 (对应 docker-compose)
    ES_HOST = os.getenv("ES_HOST", "http://localhost:9200")
    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS = os.getenv("MINIO_ACCESS", "admin")
    MINIO_SECRET = os.getenv("MINIO_SECRET", "password123")
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")

    # 业务配置
    ES_INDEX = "enterprise_kb"
    EMBEDDING_MODEL = "BAAI/bge-small-zh-v1.5" # 第一次运行会自动下载，约 100MB
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "") # 如果为空，使用 Mock 模式