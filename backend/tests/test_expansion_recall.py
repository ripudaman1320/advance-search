from backend.app.retrieval.chroma_retriever import ChromaRetriever
from backend.app.retrieval.query_expander import QueryExpander
from backend.app.config import settings

chroma = ChromaRetriever(settings.chroma_db_path)
expander = QueryExpander()

query = "status implementation"

# Without expansion
without = chroma.retrieve(query, top_k=5)
without_ids = set(r.chunk_id for r in without)

# With expansion
expanded = expander.expand(query)
with_results = []
for q in expanded:
    with_results.extend(chroma.retrieve(q, top_k=5))
with_ids = set(r.chunk_id for r in with_results)

print(f"Without expansion: {len(without_ids)} unique chunks")
print(f"With expansion: {len(with_ids)} unique chunks")
print(f"Improvement: {(len(with_ids) - len(without_ids)) / len(without_ids) * 100:.1f}%")

# Show new chunks found by expansion
new_chunks = with_ids - without_ids
print(f"\nNew chunks found: {len(new_chunks)}")
for chunk_id in list(new_chunks)[:3]:
    for r in with_results:
        if r.chunk_id == chunk_id:
            print(f"  - {r.content[:60]}...")
            break
