from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./data/email_rag.db"
    
    # Chroma
    chroma_db_path: str = "./data/.chroma"
    
    # LLM
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3:latest"
    groq_api_key: str = ""
    
    # Generation
    llm_temperature: float = 0.3
    llm_max_tokens: int = 500
    
    # Retrieval
    retrieval_top_k: int = 5
    confidence_threshold: float = 0.5
    
    # API
    api_title: str = "Email RAG Chatbot API"
    api_version: str = "0.1.0"
    
    # Environment
    environment: str = "development"
    debug: bool = True

    #CrossEncoder model for hallucination detection
    # hallucination_model_name: str = "cross-encoder/nli-roberta-base"
    # hallucination_model_name: str = "cross-encoder/nli-roberta-large"
    hallucination_model_name: str = "cross-encoder/nli-distilroberta-base"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()