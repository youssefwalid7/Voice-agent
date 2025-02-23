from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str
    aws_bucket_name: str
    database_url: str
    pinecone_api_key: str
    pinecone_index: str
    rag_exclude_phrases: list = ["hello", "hi", "hey", "how are you","thank you", "thanks", "bye", "goodbye"]
    default_retriever_k: int = 2
    max_context_length: int = 1000
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()