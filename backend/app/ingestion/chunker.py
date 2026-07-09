from langchain_text_splitters import RecursiveCharacterTextSplitter
import hashlib
from app.models.schemas import ChunkCreate, EmailDocument

class SemanticChunker:
    """Semantic chunking optimized for emails"""
    
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len,
        )
    
    def chunk(self, email: EmailDocument) -> list[ChunkCreate]:
        """Split email into semantic chunks"""
        chunks = []
        
        # Create markdown representation with metadata
        markdown_content = f"""# {email.subject}

**From**: {email.sender_email} ({email.sender_name})
**Date**: {email.created_at.isoformat()}
**Thread**: {email.thread_id}

---

{email.body}

---

**Metadata**:
- Sender Email: {email.sender_email}
- Word Count: {email.word_count}
"""
        
        # Split by semantic boundaries
        chunk_texts = self.splitter.split_text(markdown_content)
        
        for idx, content in enumerate(chunk_texts):
            # Create deterministic chunk ID
            chunk_id = hashlib.md5(
                f"{email.id}_{idx}_{content}".encode()
            ).hexdigest()[:16]
            
            chunk = ChunkCreate(
                document_id=email.id,
                content=content,
                tokens=len(content.split()),
                metadata={
                    "source_doc_id": email.id,
                    "sender": email.sender_email,
                    "timestamp": email.created_at.isoformat(),
                    "thread_id": email.thread_id,
                    "chunk_index": idx,
                    "total_chunks": len(chunk_texts),
                    "subject": email.subject,
                }
            )
            chunks.append(chunk)
        
        return chunks