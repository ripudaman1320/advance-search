from backend.app.retrieval.chroma_retriever import ChromaRetriever
from backend.app.retrieval.reranker import CrossEncoderReranker
from backend.app.retrieval.confidence_scorer import ConfidenceScorer
from backend.app.config import settings

# Load Phase 1 components
chroma = ChromaRetriever(settings.chroma_db_path)
reranker = CrossEncoderReranker()
scorer = ConfidenceScorer()

query = "What was Project Implementation Status Update?"

# Step 1: Initial retrieval
initial = chroma.retrieve(query, top_k=20)
print(f"Initial retrieval: {len(initial)} chunks")

# Step 2: Rerank
chunks = [r.content for r in initial]
reranked_tuples = reranker.rerank(query, chunks)
print(f"Reranked: {len(reranked_tuples)} chunks")

# Show top-3 before and after
print("\nTop 3 by hybrid score (before rerank):")
for r in initial[:3]:
    print(f"  {r.score:.3f}: {r.content[:50]}...")

print("\nTop 3 by cross-encoder (after rerank):")
for text, score in reranked_tuples[:3]:
    print(f"  {score:.3f}: {text[:50]}...")

# Step 3: Score confidence
print("\nWith confidence scores:")
for text, rerank_score in reranked_tuples[:3]:
    # Create mock chunk dict
    chunk = {
        'chunk_id': 'mock',
        'timestamp': '2024-06-15T10:00:00',
        'source_doc_id': 'email_1'
    }
    conf = scorer.score(chunk, search_score=rerank_score, all_results=[])
    print(f"  {conf:.3f}: {text[:50]}...")
