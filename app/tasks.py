from celery import Celery
from app.config import settings
from app.core.storage import Storage
from app.core.search import KnowledgeBase
from pypdf import PdfReader
import io

# 初始化 Celery
celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# 注册任务
@celery_app.task(bind=True)
def process_document(self, filename: str):
    """
    异步 ETL 流程：
    1. 从 MinIO 下载文件
    2. 解析 PDF
    3. 切片 & Embedding
    4. 写入 ES
    """
    print(f"🚀 [Task] Start processing: {filename}")
    
    try:
        # 1. 从 MinIO 获取文件流
        storage = Storage()
        response = storage.get_object(filename)
        file_data = response.read()
        response.close()
        response.release_conn()

        # 2. 解析 (这里简化处理，只做 PDF)
        text = ""
        if filename.endswith(".pdf"):
            pdf_file = io.BytesIO(file_data)
            reader = PdfReader(pdf_file)
            for page in reader.pages:
                text += page.extract_text()
        else:
            text = file_data.decode("utf-8")

        # 3. 切片 (简单按字符切，生产环境用 LangChain Splitter)
        chunk_size = 300
        kb = KnowledgeBase()
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        
        # 4. 入库
        for chunk in chunks:
            kb.insert(chunk, filename)
            
        return f"✅ Success: Indexed {len(chunks)} chunks."

    except Exception as e:
        print(f"❌ [Task] Error: {e}")
        raise e