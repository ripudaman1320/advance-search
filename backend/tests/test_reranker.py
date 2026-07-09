# from backend.app.retrieval.reranker import CrossEncoderReranker

# reranker = CrossEncoderReranker()

# query = "What is the status of project X?"
# chunks = [
#     "Project X implementation is on track with 85% completion.",
#     "The weather today is sunny.",
#     "Project X budget was approved by management last week.",
#     "Python is a great programming language.",
#     "Project X deadline is next Friday.",
# ]

# results = reranker.rerank(query, chunks)

# print(f"Query: {query}\n")
# for i, (chunk, score) in enumerate(results, 1):
#     print(f"{i}. [{score:.3f}] {chunk[:60]}...")

from backend.app.storage.database import DatabaseManager
from backend.app.config import settings
from backend.app.retrieval.reranker import CrossEncoderReranker

db = DatabaseManager(settings.database_url)
emails = db.list_emails()

if emails:
    print(f'Found {len(emails)} emails in database')
    
    # Get first email body
    first_email = db.get_email(emails[0]['id'])
    # print(f'Testing with: {first_email[\"subject\"]}')
    
    # Chunk it
    from backend.app.ingestion.chunker import SemanticChunker
    from backend.app.models.schemas import EmailDocument
    
    email_doc = EmailDocument(**first_email)
    chunker = SemanticChunker()
    chunks = chunker.chunk(email_doc)
    
    # Rerank
    reranker = CrossEncoderReranker()
    chunk_texts = [c.content for c in chunks]
    
    query = 'What is the main topic?'
    results = reranker.rerank(query, chunk_texts[:5])
    
    print(f'\\nReranked {len(results)} chunks for query: {query}')
    for i, (text, score) in enumerate(results, 1):
        print(f'{i}. [{score:.3f}] {text[:50]}...')