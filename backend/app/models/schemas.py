from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

# ============= EMAIL MODELS =============

class EmailDocumentCreate(BaseModel):
    """Input model for email ingestion"""
    subject: str
    sender_email: str
    sender_name: Optional[str] = None
    body: str
    timestamp: Optional[datetime] = None

class EmailDocument(EmailDocumentCreate):
    """Stored email document with metadata"""
    id: str
    thread_id: str
    word_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============= CHUNK MODELS =============

class ChunkMetadata(BaseModel):
    """Metadata for a semantic chunk"""
    source_doc_id: str
    sender: str
    timestamp: str
    thread_id: str
    chunk_index: int
    total_chunks: int

class ChunkCreate(BaseModel):
    """Chunk to be stored in Chroma"""
    document_id: str
    content: str
    tokens: int
    metadata: dict

# ============= RETRIEVAL MODELS =============

class RetrievalResult(BaseModel):
    """Single retrieved chunk with scoring"""
    chunk_id: str
    content: str
    score: float
    confidence: float
    source_doc_id: str
    sender: str
    timestamp: str
    
class RetrieverConfig(BaseModel):
    """Retriever configuration"""
    top_k: int = 5
    confidence_threshold: float = 0.5
    use_reranking: bool = True

# ============= QUERY & RESPONSE MODELS =============

class ChatQuery(BaseModel):
    """User query"""
    text: str
    top_k: int = 5
    return_sources: bool = True

class ChatResponse(BaseModel):
    """RAG response"""
    answer: str
    sources: List[RetrievalResult]
    confidence: float
    execution_time_ms: float
    fallback_used: bool = False
    insufficient_evidence: Optional[str] = None
    
    # Phase 3 additions:
    hallucination_detected: bool = False
    validation_coverage: float = 1.0  # 0-1 range

# ============= INGESTION MODELS =============

class IngestResponse(BaseModel):
    """Ingestion result"""
    email_id: str
    subject: str
    chunks_created: int
    status: str
    message: str

# ============= EVALUATION MODELS =============

class EvalResult(BaseModel):
    """Evaluation metrics"""
    query: str
    answer: str
    mrr: Optional[float] = None
    confidence: float
    retrieved_count: int
    timestamp: datetime