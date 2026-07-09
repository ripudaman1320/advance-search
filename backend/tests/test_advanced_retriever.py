from backend.app.retrieval.advanced_retriever import AdvancedRetriever
from backend.app.config import settings
import time

retriever = AdvancedRetriever(
    chroma_db_path=settings.chroma_db_path,
    use_reranking=True,
    use_expansion=True,
    confidence_threshold=0.5
)

query = "What is the main topic of the emails?"

# Time the retrieval
start = time.time()
results = retriever.retrieve(query, top_k=5)
elapsed = time.time() - start

print(f"Query: {query}")
print(f"Time: {elapsed:.3f}s")
print(f"Results: {len(results)}")

for i, result in enumerate(results, 1):
    print(f"\n{i}. Confidence: {result.confidence:.3f}")
    print(f"   Sender: {result.sender}")
    print(f"   Content: {result.content[:80]}...")
