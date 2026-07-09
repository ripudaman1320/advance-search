from backend.app.retrieval.chroma_retriever import ChromaRetriever
from backend.app.retrieval.advanced_retriever import AdvancedRetriever
from backend.app.config import settings
import time

query = "What was discussed?"

# Phase 1 (basic hybrid retrieval)
start = time.time()
phase1 = ChromaRetriever(settings.chroma_db_path)
results_p1 = phase1.retrieve(query, top_k=5)
time_p1 = time.time() - start

# Phase 2 (advanced with reranking)
start = time.time()
phase2 = AdvancedRetriever(settings.chroma_db_path)
results_p2 = phase2.retrieve(query, top_k=5)
time_p2 = time.time() - start

print(f"Query: {query}\n")

print("PHASE 1 (Basic):")
print(f"  Time: {time_p1:.3f}s")
print(f"  Avg Confidence: {sum(r.confidence for r in results_p1)/len(results_p1):.3f}")

print("\nPHASE 2 (Advanced):")
print(f"  Time: {time_p2:.3f}s")
print(f"  Avg Confidence: {sum(r.confidence for r in results_p2)/len(results_p2):.3f}")

print(f"\nSlowdown: {(time_p2 / time_p1 - 1) * 100:.0f}% (expected: 50-100%)")
print(f"Confidence improvement: {(sum(r.confidence for r in results_p2) - sum(r.confidence for r in results_p1)) / len(results_p1):.3f}")

# Show ranking differences
print("\n--- Ranking Changes ---")
ids_p1 = [r.chunk_id for r in results_p1]
ids_p2 = [r.chunk_id for r in results_p2]

for i, id in enumerate(ids_p2, 1):
    if id in ids_p1:
        old_rank = ids_p1.index(id) + 1
        print(f"  Chunk {id}: rank {old_rank} → {i}")
    else:
        print(f"  Chunk {id}: new in top-5")
