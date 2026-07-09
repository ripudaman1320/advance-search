from datetime import datetime, timedelta
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class ConfidenceScorer:
    """Multi-factor confidence scoring for retrieved chunks"""
    
    def __init__(
        self,
        freshness_weight: float = 0.30,
        retrieval_weight: float = 0.40,
        overlap_weight: float = 0.20,
        consistency_weight: float = 0.10
    ):
        """
        Initialize confidence scorer with weights
        
        Args:
            freshness_weight: Weight for recency (default: 0.30)
            retrieval_weight: Weight for search score (default: 0.40)
            overlap_weight: Weight for source overlap (default: 0.20)
            consistency_weight: Weight for consistency (default: 0.10)
        """
        self.weights = {
            'freshness': freshness_weight,
            'retrieval': retrieval_weight,
            'overlap': overlap_weight,
            'consistency': consistency_weight
        }
        
        # Verify weights sum to 1.0
        total = sum(self.weights.values())
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total}")
        
        logger.info(f"Confidence scorer initialized with weights: {self.weights}")
    
    def score_freshness(self, timestamp_str: str) -> float:
        """
        Score based on email recency
        
        Args:
            timestamp_str: ISO format timestamp string
        
        Returns:
            Score 0-1 (1 = recent, 0 = very old)
        """
        try:
            timestamp = datetime.fromisoformat(timestamp_str)
            days_old = (datetime.utcnow() - timestamp).days
            
            # Linear decay over 1 year
            freshness = max(0, 1 - (days_old / 365))
            return float(freshness)
        except Exception as e:
            logger.warning(f"Could not parse timestamp {timestamp_str}: {e}")
            return 0.5  # Neutral default
    
    def score_retrieval(self, search_score: float) -> float:
        """
        Score based on retrieval/reranking score
        
        Args:
            search_score: Score from 0-1
        
        Returns:
            Score 0-1
        """
        # Already normalized from hybrid search + reranking
        return max(0, min(search_score, 1.0))
    
    def score_overlap(self, chunk_id: str, all_results: List[Dict]) -> float:
        """
        Score based on how many similar chunks from same source
        
        Args:
            chunk_id: ID of current chunk
            all_results: All retrieved results
        
        Returns:
            Score 0-1 (more overlap = higher score)
        """
        # Get source doc ID from chunk
        source_id = None
        for result in all_results:
            if result.get('chunk_id') == chunk_id:
                source_id = result.get('source_doc_id')
                break
        
        if not source_id:
            return 0.5  # Neutral if can't determine
        
        # Count chunks from same source in top results
        same_source_count = sum(
            1 for r in all_results[:10]
            if r.get('source_doc_id') == source_id
        )
        
        # Normalize: 1-3 chunks = 0.5, 4+ chunks = 1.0
        overlap = min(same_source_count / 4, 1.0)
        return float(overlap)
    
    def score_consistency(self, chunk_id: str) -> float:
        """
        Score based on consistency across multiple retrievals
        
        Note: Requires running query twice and comparing results
        Not implemented in Phase 2, returns neutral default
        
        Args:
            chunk_id: Chunk identifier
        
        Returns:
            Score 0-1
        """
        # TODO: Implement in Phase 3 with persistent retrieval cache
        return 0.5  # Neutral default
    
    def score(
        self,
        chunk: Dict,
        search_score: float,
        all_results: List[Dict]
    ) -> float:
        """
        Calculate combined confidence score
        
        Args:
            chunk: Dictionary with metadata (must have 'timestamp', 'chunk_id')
            search_score: Score from hybrid search + reranking (0-1)
            all_results: All retrieved results for overlap calculation
        
        Returns:
            Combined confidence score (0-1)
        """
        # Calculate individual scores
        freshness = self.score_freshness(chunk.get('timestamp', ''))
        retrieval = self.score_retrieval(search_score)
        overlap = self.score_overlap(chunk.get('chunk_id', ''), all_results)
        consistency = self.score_consistency(chunk.get('chunk_id', ''))
        
        # Combine with weights
        confidence = (
            self.weights['freshness'] * freshness +
            self.weights['retrieval'] * retrieval +
            self.weights['overlap'] * overlap +
            self.weights['consistency'] * consistency
        )
        
        return float(confidence)