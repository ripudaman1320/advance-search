import numpy as np
from typing import List

class RetrievalMetrics:
    """Compute standard IR metrics"""
    
    @staticmethod
    def mrr(ranking: List[bool]) -> float:
        """Mean Reciprocal Rank: position of first relevant"""
        for i, is_relevant in enumerate(ranking, 1):
            if is_relevant:
                return 1.0 / i
        return 0.0
    
    @staticmethod
    def ndcg(relevances: List[float], k: int = 5) -> float:
        """Normalized Discounted Cumulative Gain"""
        dcg = sum(rel / np.log2(i + 2) for i, rel in enumerate(relevances[:k]))
        idcg = sum(1 / np.log2(i + 2) for i in range(min(k, len(relevances))))
        return dcg / idcg if idcg > 0 else 0.0
    
    @staticmethod
    def precision_at_k(retrieved: List[bool], k: int = 5) -> float:
        """Precision@k: fraction of retrieved that are relevant"""
        return sum(retrieved[:k]) / k if k > 0 else 0.0
    
    @staticmethod
    def recall_at_k(retrieved: List[bool], total_relevant: int, k: int = 5) -> float:
        """Recall@k: fraction of relevant that are retrieved"""
        return sum(retrieved[:k]) / total_relevant if total_relevant > 0 else 0.0
