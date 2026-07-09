from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.config import settings
from app.storage.database import DatabaseManager
# from app.retrieval.chroma_retriever import ChromaRetriever
from app.retrieval.advanced_retriever import AdvancedRetriever
from app.core.llm import OllamaLLMClient
from app.api import routes
from app.core.hallucination_detector import HallucinationDetector
from app.generation.response_validator import ResponseValidator
from app.generation.fallback_handler import FallbackHandler

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="Email RAG Chatbot - Production Grade RAG System"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
db_manager: DatabaseManager = None
# retriever: ChromaRetriever = None
retriever: AdvancedRetriever = None
llm_client: OllamaLLMClient = None

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    global db_manager, retriever, llm_client
    
    logger.info("🚀 Starting Email RAG Chatbot...")
    
    # Initialize database
    logger.info(f"📦 Initializing database: {settings.database_url}")
    db_manager = DatabaseManager(settings.database_url)
    db_manager.init_db()
    
    # Initialize retriever
    logger.info(f"🔍 Initializing Chroma retriever: {settings.chroma_db_path}")
    # retriever = ChromaRetriever(settings.chroma_db_path)
    retriever = AdvancedRetriever(
    chroma_db_path=settings.chroma_db_path,
    use_reranking=True,
    use_expansion=True,
    confidence_threshold=settings.confidence_threshold
    )
    # Initialize LLM
    logger.info(f"🤖 Connecting to Ollama: {settings.ollama_base_url}")
    llm_client = OllamaLLMClient()
    
    # Check LLM health
    ollama_ok = await llm_client.health_check()
    if not ollama_ok:
        logger.warning("⚠️  Ollama not running! Chat will fail. Start Ollama first:")
        logger.warning(f"   ollama run {settings.ollama_model}")
    else:
        logger.info(f"✓ Ollama connected ({settings.ollama_model})")

    hallucination_detector = HallucinationDetector()
    response_validator = ResponseValidator()
    fallback_handler = FallbackHandler()

    # Set routes dependencies
    routes.set_dependencies(db_manager, retriever, llm_client, hallucination_detector, response_validator, fallback_handler)
    
    logger.info("✓ Startup complete!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down...")

# Include routes
app.include_router(routes.router, prefix="/api", tags=["email-rag"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )

