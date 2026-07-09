import email

from app.generation.fallback_handler import FallbackHandler
from app.core.hallucination_detector import HallucinationDetector
from app.generation.response_validator import ResponseValidator
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
import time
import asyncio
from datetime import datetime
import logging

from app.models.schemas import (
    ChatQuery,
    ChatResponse,
    IngestResponse,
    RetrievalResult,
)
from app.config import settings
from app.storage.database import DatabaseManager
from app.ingestion.docx_parser import DOCXEmailParser
from app.ingestion.chunker import SemanticChunker
# from app.retrieval.chroma_retriever import ChromaRetriever
from app.retrieval.advanced_retriever import AdvancedRetriever
from app.core.llm import OllamaLLMClient
from app.generation.response_builder import ResponseBuilder

logger = logging.getLogger(__name__)
router = APIRouter()

# Global instances (initialized in main.py)
db_manager: DatabaseManager = None
# retriever: ChromaRetriever = None
retriever: AdvancedRetriever = None
llm_client: OllamaLLMClient = None
hallucination_detector: HallucinationDetector = None
response_validator: ResponseValidator = None
fallback_handler: FallbackHandler = None

def set_dependencies(db, ret, llm, hallucination_det, resp_val, fall_det):
    """Set global dependencies (called from main.py)"""
    global db_manager, retriever, llm_client, hallucination_detector, response_validator, fallback_handler
    db_manager = db
    retriever = ret
    llm_client = llm
    hallucination_detector = hallucination_det
    response_validator = resp_val
    fallback_handler = fall_det

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    ollama_ok = await llm_client.health_check()
    
    return JSONResponse(
        status_code=200,
        content={
            "status": "ok",
            "service": "email-rag-backend",
            "ollama": "connected" if ollama_ok else "disconnected",
            "timestamp": datetime.utcnow().isoformat(),
        }
    )

@router.post("/chat", response_model=ChatResponse)
async def chat(query: ChatQuery) -> ChatResponse:
    """Main RAG chat endpoint"""
    start_time = time.time()
    response_builder = ResponseBuilder()
    
    try:
        # Retrieve relevant chunks
        retrieved = retriever.retrieve(query.text, top_k=query.top_k)
        
        # Filter by confidence threshold
        confident_chunks = [
            r for r in retrieved 
            if r.confidence >= settings.confidence_threshold
        ]
        
        logger.info(f"Retrieved {len(retrieved)} chunks, {len(confident_chunks)} above confidence threshold")
        logger.info(f"Confident chunks ==>: {confident_chunks}")  # Debugging output
        
        if not confident_chunks:
            return ChatResponse(
                answer="I don't have enough information in your emails to answer this question.",
                sources=[],
                confidence=0.0,
                execution_time_ms=int((time.time() - start_time) * 1000),
                fallback_used=True,
                insufficient_evidence="Low retrieval confidence"
            )
        
        # Generate answer using LLM
        context_texts = [r.content for r in confident_chunks]
        logger.info(f"Context texts: {context_texts}")  # Debugging output

        answer = await llm_client.generate(query.text, context_texts)
        logger.info(f"<====LLM Answer====>: {answer}") 

        context = "\n\n".join(context_texts)
        logger.info(f"Context : {context}")  # Debugging output
        
        # Calculate average confidence
        avg_confidence = sum(r.confidence for r in confident_chunks) / len(confident_chunks)
        logger.info(f"Average confidence: {avg_confidence}")  # Debugging output
        
        print("="*60)
        built_response = response_builder.build(answer, confident_chunks)
        logger.info(f"Built response: {built_response}")  # Debugging output

        formatted_response = response_builder.format_for_ui(built_response)
        logger.info(f"Formatted response: {formatted_response}")  # Debugging output
        
        hallucination_result = hallucination_detector.detect(formatted_response, context)
        logger.info(f"Hallucination detection result: {hallucination_result}")

        # response_validation_result = response_validator.validate(formatted_response, confident_chunks)
        validation_result = response_validator.validate(
                                formatted_response,
                                # [{'content': r.content} for r in confident_chunks]
                                context
                            )
        logger.info(f"Response validation result |==>: {validation_result}")

        should_fallback, fallback_reason = fallback_handler.should_fallback(
                                                hallucination_result,
                                                avg_confidence,
                                                validation_result
                                            )
        
        print(f"Fallback decision printing: {should_fallback}, Reason: {fallback_reason}")
        logger.info(f"Fallback decision: {should_fallback}, Reason: {fallback_reason}")
        
        final_answer = fallback_handler.get_fallback_response(fallback_reason) if should_fallback else formatted_response
        logger.info(f"||~~~Final answer~~~||: {final_answer}")
        # return ChatResponse(
        #     answer=final_answer,
        #     sources=confident_chunks if query.return_sources else [],
        #     confidence=avg_confidence,
        #     execution_time_ms=int((time.time() - start_time) * 1000),
        # )
        return ChatResponse(
        answer=final_answer,
        sources=retrieved,
        confidence=avg_confidence,
        execution_time_ms=int((time.time() - start_time) * 1000),
        fallback_used=should_fallback,
        reason_insufficient_evidence=fallback_reason if should_fallback else None,
        hallucination_detected=hallucination_result.get('is_hallucinated'),
        validation_coverage=validation_result.get('coverage')
        )
    
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ingest", response_model=IngestResponse)
async def ingest_email(docx_path: str) -> IngestResponse:
    """Ingest a new email from DOCX file"""
    
    try:
        # Parse DOCX
        email_data = DOCXEmailParser.parse_from_path(docx_path)
        print(email_data.subject)  # Should print subject
        print(email_data.sender_email)  # Should print email
        
        # Generate thread ID
        thread_id = f"{email_data.sender_email}_{email_data.timestamp.strftime('%Y%m%d')}"
        
        # Add to database
        email_dict = {
            "subject": email_data.subject,
            "sender_email": email_data.sender_email,
            "sender_name": email_data.sender_name,
            "body": email_data.body,
            "thread_id": thread_id,
            "created_at": email_data.timestamp,
        }
        email_id = db_manager.add_email(email_dict)
        
        # Get full email from DB
        email_full = db_manager.get_email(email_id)
        
        # Chunk the email
        from app.models.schemas import EmailDocument
        email_doc = EmailDocument(**email_full)
        chunker = SemanticChunker()
        chunks = chunker.chunk(email_doc)
        
        # Convert to format for retriever
        chunks_data = [
            {
                "content": chunk.content,
                "metadata": chunk.metadata,
            }
            for chunk in chunks
        ]
        
        # Add to Chroma
        retriever.add_chunks(chunks_data)
        
        logger.info(f"Ingested email: {email_data.subject} ({len(chunks)} chunks)")
        
        return IngestResponse(
            email_id=email_id,
            subject=email_data.subject,
            chunks_created=len(chunks),
            status="success",
            message=f"Email '{email_data.subject}' ingested successfully with {len(chunks)} chunks"
        )
    
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ingestion error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/emails")
async def list_emails():
    """List all ingested emails"""
    try:
        emails = db_manager.list_emails()
        return {
            "count": len(emails),
            "emails": emails
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))