from backend.tests.test_rerank_confidence import *
from backend.app.retrieval.pipeline_v2 import rerank_and_score

scored = rerank_and_score(query, initial, reranker, scorer)
print(f'Scored {len(scored)} results')
for r in scored[:3]:
    print(f'  {r.confidence:.3f}: {r.content[:50]}...')