from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List

from config import Config

class KnowledgeBase:
    def __init__(self):
        self.es = Elasticsearch(Config.ES_HOST)
        print("[System] Loading Embedding Model... (First time takes time)")
        self.model = SentenceTransformer(Config.EMBEDDING_MODEL)
        self._init_index()

    def _init_index(self):
        if not self.es.indices.exists(index=Config.ES_INDEX):
            mapping = {
                "mappings": {
                    "properties": {
                        "content": {"type": "text", "analyzer": "ik_max_word"}, # 需安装IK插件，未安装ES会报错，可用 standard
                        "embedding": {
                            "type": "dense_vector",
                            "dims": 512, # bge-small 是 512 维
                            "index": True,
                            "similarity": "cosine"
                        },
                        "source": {"type": "keyword"}
                    }
                }
            }
            # 如果没有IK分词器，回退到标准分词
            try:
                self.es.indices.create(index=Config.ES_INDEX, body=mapping)
            except Exception:
                mapping["mappings"]["properties"]["content"]["analyzer"] = "standard"
                self.es.indices.create(index=Config.ES_INDEX, body=mapping)
            print(f"[KB] Index {Config.ES_INDEX} created.")

    def ingest_document(self, file_path: str, minio_url: str):
        # 1. 解析
        text = ""
        if file_path.endswith(".pdf"):
            reader = PdfReader(file_path)
            for page in reader.pages:
                text += page.extract_text()
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()

        # 2. 切片 (LangChain Splitter)
        splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
        chunks = splitter.split_text(text)

        # 3. 向量化并入库
        print(f"[KB] Processing {len(chunks)} chunks...")
        for i, chunk in enumerate(chunks):
            vec = self.model.encode(chunk).tolist()
            doc = {
                "content": chunk,
                "embedding": vec,
                "source": minio_url,
                "chunk_id": i
            }
            self.es.index(index=Config.ES_INDEX, document=doc)
        self.es.indices.refresh(index=Config.ES_INDEX)
        print(f"[KB] Ingestion complete for {file_path}")

    def search(self, query: str, top_k=3) -> List[str]:
        vec = self.model.encode(query).tolist()
        # 混合检索 DSL
        body = {
            "size": top_k,
            "query": {
                "bool": {
                    "should": [
                        {"match": {"content": query}}, # 关键词匹配
                        {
                            "knn": {
                                "field": "embedding",
                                "query_vector": vec,
                                "k": top_k,
                                "num_candidates": 100
                            }
                        }
                    ]
                }
            }
        }
        res = self.es.search(index=Config.ES_INDEX, body=body)
        return [hit["_source"]["content"] for hit in res["hits"]["hits"]]