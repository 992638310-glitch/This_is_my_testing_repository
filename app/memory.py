import json
import redis
from typing import List, Dict

from config import Config

class MemoryManager:
    def __init__(self):
        self.r = redis.Redis(host=Config.REDIS_HOST, port=6379, db=0, decode_responses=True)
        self.window_size = 6 #保留最近6条记录

    def add_history(self, session_id: str, role: str, content: str):
        key = f"chat_history:{session_id}"
        msg = json.dumps({"role": role, "content": content})
        self.r.rpush(key, msg)
        # 滑动窗口截断
        if self.r.llen(key) > self.window_size:
            self.r.lpop(key)

    def get_history(self, session_id: str) -> List[Dict]:
        key = f"chat_history:{session_id}"
        items = self.r.lrange(key, 0, -1)
        return [json.loads(i) for i in items]