import os
import time
from minio import Minio

from config import Config

class StorageManager:
    def __init__(self):
        self.client = Minio(
            Config.MINIO_ENDPOINT,
            access_key=Config.MINIO_ACCESS,
            secret_key=Config.MINIO_SECRET,
            secure=False
        )
        self.bucket = "raw-documents"
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    def upload_file(self, file_path: str) -> str:
        file_name = os.path.basename(file_path)
        # 使用哈希防止重名覆盖
        object_name = f"{int(time.time())}_{file_name}"
        self.client.fput_object(self.bucket, object_name, file_path)
        print(f"[Storage] File uploaded: {object_name}")
        return f"s3://{self.bucket}/{object_name}"