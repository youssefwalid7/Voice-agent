from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from app.config.settings import settings

class VectorDBService:
    def __init__(self):
        self._init_pinecone()
        
    def _init_pinecone(self):        
        self.pc = Pinecone(api_key=settings.pinecone_api_key)
        self.index = self.pc.Index(settings.pinecone_index)
        self.embeddings = OpenAIEmbeddings(openai_api_key=settings.openai_api_key, model="text-embedding-ada-002")
        
    def get_vector_store(self):
        return PineconeVectorStore(
            index=self.index,
            embedding=self.embeddings
        )

vector_db_service = VectorDBService()