def rerank_and_score(query, initial_results, reranker, scorer):
    """Helper: rerank and score in one go"""
    # Rerank
    chunks = [r.content for r in initial_results]
    reranked = reranker.rerank(query, chunks)
    
    # Score confidence
    scored = []
    for text, score in reranked:
        # Match back to original result
        for orig in initial_results:
            if orig.content == text:
                conf = scorer.score(
                    {
                        'chunk_id': orig.chunk_id,
                        'timestamp': orig.timestamp,
                        'source_doc_id': orig.source_doc_id
                    },
                    search_score=score,
                    all_results=[{
                        'chunk_id': r.chunk_id,
                        'source_doc_id': r.source_doc_id
                    } for r in initial_results]
                )
                orig.confidence = conf
                scored.append(orig)
                break
    
    return scored
