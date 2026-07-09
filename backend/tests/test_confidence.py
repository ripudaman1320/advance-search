from backend.app.retrieval.confidence_scorer import ConfidenceScorer
from datetime import datetime, timedelta

scorer = ConfidenceScorer()

# Test 1: Freshness scoring
print("=== FRESHNESS SCORING ===")
today = datetime.utcnow().isoformat()
one_month_ago = (datetime.utcnow() - timedelta(days=30)).isoformat()
one_year_ago = (datetime.utcnow() - timedelta(days=365)).isoformat()

print(f"Today: {scorer.score_freshness(today):.3f}")
print(f"1 month ago: {scorer.score_freshness(one_month_ago):.3f}")
print(f"1 year ago: {scorer.score_freshness(one_year_ago):.3f}")

# Test 2: Retrieval scoring
print("\n=== RETRIEVAL SCORING ===")
print(f"Score 0.0: {scorer.score_retrieval(0.0):.3f}")
print(f"Score 0.5: {scorer.score_retrieval(0.5):.3f}")
print(f"Score 0.9: {scorer.score_retrieval(0.9):.3f}")

# Test 3: Overlap scoring
print("\n=== OVERLAP SCORING ===")
all_results = [
    {'chunk_id': 'c1', 'source_doc_id': 'email_1'},
    {'chunk_id': 'c2', 'source_doc_id': 'email_1'},
    {'chunk_id': 'c3', 'source_doc_id': 'email_1'},
    {'chunk_id': 'c4', 'source_doc_id': 'email_2'},
]
print(f"3 chunks from same source: {scorer.score_overlap('c1', all_results):.3f}")

# Test 4: Combined score
print("\n=== COMBINED SCORE ===")
chunk = {
    'chunk_id': 'c1',
    'timestamp': datetime.utcnow().isoformat(),
    'source_doc_id': 'email_1'
}
confidence = scorer.score(chunk, search_score=0.8, all_results=all_results)
print(f"Combined confidence: {confidence:.3f}")
