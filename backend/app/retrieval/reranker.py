import logging
from sentence_transformers import CrossEncoder
from typing import List, Tuple

logger = logging.getLogger(__name__)

class CrossEncoderReranker:
    def __init__(self):
        # self.model = CrossEncoder('cross-encoder/mmarco-MiniLMv2-L12-H384-v1')
        print("Initializing CrossEncoderReranker")
        logger.info("Initializing CrossEncoderReranker")
        # self.model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-12-v2')
        self.model = CrossEncoder('cross-encoder/qnli-distilroberta-base')
    
    def rerank(self, query: str, chunks: List[str]) -> List[Tuple[str, float]]:
        """
        Rerank chunks by relevance to query
        Returns: [(chunk, score), ...] sorted by score
        """
        logger.info(f"Reranking {len(chunks)} chunks for query: {query}")
        pairs = [[query, chunk] for chunk in chunks]
        scores = self.model.predict(pairs)
        # scores are raw logits, normalize them
        normalized = (scores - scores.min()) / (scores.max() - scores.min() + 1e-6)
        return list(zip(chunks, normalized))