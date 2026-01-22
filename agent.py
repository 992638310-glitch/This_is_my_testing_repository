import os

from config import Config
from storage import StorageManager
from memory import MemoryManager
from knowledge_base import KnowledgeBase
from llm_service import LLMService

class Agent:
    def __init__(self):
        self.storage = StorageManager()
        self.memory = MemoryManager()
        self.kb = KnowledgeBase()
        self.llm = LLMService()

    def handle_upload(self, file_path):
        if not os.path.exists(file_path):
            return "❌ 文件不存在"
        try:
            url = self.storage.upload_file(file_path)
            self.kb.ingest_document(file_path, url)
            return "✅ 知识库构建完成！"
        except Exception as e:
            return f"❌ 处理失败: {str(e)}"

    def handle_chat(self, session_id, query):
        # 1. 查历史
        history = self.memory.get_history(session_id)

        # 2. 查知识库 (RAG)
        contexts = self.kb.search(query)
        context_str = "\n".join([f"- {c}" for c in contexts])

        # 3. 组装 Prompt
        system_prompt = f"""
        你是一个企业级智能助手。请基于以下上下文回答用户问题。
        如果上下文没有相关信息，请诚实说不知道。

        【参考知识库】：
        {context_str}
        """

        # 4. 生成回答
        print(f"\n🔍 [Debug] Retrieved Contexts: {len(contexts)}")
        answer = self.llm.chat(system_prompt, history, query)

        # 5. 存入记忆
        self.memory.add_history(session_id, "user", query)
        self.memory.add_history(session_id, "assistant", answer)

        return answer