from typing import List, Dict, Optional
import logging
from datetime import datetime

from app.retrieval.chroma_retriever import ChromaRetriever
from app.retrieval.reranker import CrossEncoderReranker
from app.retrieval.confidence_scorer import ConfidenceScorer
from app.retrieval.query_expander import QueryExpander
from app.models.schemas import RetrievalResult

logger = logging.getLogger(__name__)

class AdvancedRetriever:
    """Advanced retrieval pipeline with reranking and confidence scoring"""
    
    def __init__(
        self,
        chroma_db_path: str,
        use_reranking: bool = True,
        use_expansion: bool = True,
        confidence_threshold: float = 0.5
    ):
        """
        Initialize advanced retriever with all components
        
        Args:
            chroma_db_path: Path to Chroma database
            use_reranking: Enable cross-encoder reranking
            use_expansion: Enable query expansion
            confidence_threshold: Minimum confidence to include result
        """
        self.chroma_retriever = ChromaRetriever(chroma_db_path)
        self.reranker = CrossEncoderReranker() if use_reranking else None
        self.confidence_scorer = ConfidenceScorer()
        self.query_expander = QueryExpander() if use_expansion else None
        self.confidence_threshold = confidence_threshold
        
        logger.info(
            f"Advanced retriever initialized: "
            f"reranking={use_reranking}, expansion={use_expansion}"
        )
    
    def add_chunks(self, chunks: list[dict]):
        """Add chunks to the underlying Chroma retriever"""
        self.chroma_retriever.add_chunks(chunks)
    
    def retrieve(
        self,
        query: str,
        top_k: int = 5
    ) -> List[RetrievalResult]:
        """
        Retrieve and rank results using advanced pipeline
        
        Args:
            query: User query
            top_k: Number of top results to return
        
        Returns:
            List of RetrievalResult objects sorted by confidence
        """
        logger.info(f"Advanced retrieval for query: {query}")
        
        # Step 1: Expand query
        if self.query_expander:
            expanded_queries = self.query_expander.expand(query)
            logger.info(f"Query expanded to {len(expanded_queries)} variations")
        else:
            expanded_queries = [query]
        
        # Step 2: Hybrid search with all variations
        all_results_raw = []
        for expanded_q in expanded_queries:
            results = self.chroma_retriever.retrieve(expanded_q, top_k=20)
            all_results_raw.extend(results)
            logger.debug(f"Retrieved {len(results)} results for variation: {expanded_q[:50]}...")
        
        if not all_results_raw:
            logger.warning("No results found")
            return []
        
        # Step 3: Deduplicate by chunk_id
        seen = {}
        for result in all_results_raw:
            if result.chunk_id not in seen:
                seen[result.chunk_id] = result
        
        unique_results = list(seen.values())
        logger.info(f"Deduplicated to {len(unique_results)} unique chunks")
        
        # Step 4: Rerank with cross-encoder
        if self.reranker:
            chunks_text = [r.content for r in unique_results]
            reranked_tuples = self.reranker.rerank(query, chunks_text)
            
            # Map back to results with new scores
            reranked_results = []
            for chunk_text, rerank_score in reranked_tuples:
                # Find original result
                for result in unique_results:
                    if result.content == chunk_text:
                        result.score = rerank_score  # Update score
                        reranked_results.append(result)
                        break
            
            unique_results = reranked_results
            logger.info(f"Reranked {len(unique_results)} results")
        
        # Step 5: Score confidence
        scored_results = []
        for result in unique_results:
            confidence = self.confidence_scorer.score(
                chunk={
                    'chunk_id': result.chunk_id,
                    'timestamp': result.timestamp,
                    'source_doc_id': result.source_doc_id
                },
                search_score=result.score,
                all_results=[
                    {
                        'chunk_id': r.chunk_id,
                        'source_doc_id': r.source_doc_id,
                        'timestamp': r.timestamp
                    }
                    for r in unique_results
                ]
            )
            
            result.confidence = confidence
            scored_results.append(result)
        
        logger.info(f"Scored {len(scored_results)} results with confidence")
        
        # Step 6: Filter by confidence threshold
        filtered = [r for r in scored_results if r.confidence >= self.confidence_threshold]
        logger.info(f"Filtered to {len(filtered)} results above threshold {self.confidence_threshold}")
        
        # Step 7: Sort by confidence and return top-k
        filtered.sort(key=lambda x: x.confidence, reverse=True)
        final_results = filtered[:top_k]
        
        logger.info(f"Returning {len(final_results)} final results")
        
        return final_results
    
    def retrieve_with_explanation(
        self,
        query: str,
        top_k: int = 5
    ) -> Dict:
        """
        Retrieve results with detailed explanation of scoring
        
        Args:
            query: User query
            top_k: Number of top results
        
        Returns:
            Dictionary with results and explanation
        """
        results = self.retrieve(query, top_k)
        
        return {
            "results": results,
            "explanation": {
                "query": query,
                "total_retrieved": len(results),
                "confidence_threshold": self.confidence_threshold,
                "pipeline": {
                    "expansion": bool(self.query_expander),
                    "reranking": bool(self.reranker),
                    "confidence_scoring": True
                }
            }
        }