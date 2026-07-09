from sentence_transformers import CrossEncoder
from typing import Tuple
import logging
import numpy as np
from app.config import settings

logger = logging.getLogger(__name__)

class HallucinationDetector:
    """Detect hallucinations in LLM responses"""
    
    # def __init__(self, model_name: str = "cross-encoder/nli-deberta-v3-small"):
    def __init__(self, model_name: str = None): #"cross-encoder/nli-deberta-v3-base"):
        """
        Initialize the hallucination detector
        """
        self.model = CrossEncoder(model_name or settings.hallucination_model_name)
        self.hallucination_threshold = 0.5 # Try: 0.4 (more sensitive) or 0.6 (more lenient)
    
    def detect(
        self,
        response: str,
        context: str,
        threshold: float = None
    ) -> dict:
        """
        Detect if response contradicts context
        
        Returns:
            {
                'is_hallucinated': bool,
                'contradiction_score': float (0-1),
                'confidence': float,
                'reasoning': str
            }
        """
        threshold = threshold or self.hallucination_threshold
        
        logger.info(f"Context and response for hallucination detection:\nContext: {context}\nResponse: {response}")

        # NLI model returns: [contradiction, neutral, entailment]
        scores = self.model.predict([[context, response]])[0]
        
        # scores ~ [-5, 5] range
        # Normalize: negative = contradiction, positive = entailment
        # contradiction_score = 1 / (1 + np.exp(scores[0]))  # Sigmoid
        probs = np.exp(scores) / np.exp(scores).sum()
        contradiction_score = float(probs[0])
        logger.info(f"Contradiction score: {contradiction_score:.3f} (threshold: {threshold})")
        is_hallucinated = contradiction_score > threshold
        
        logger.info(
            f"Hallucination check: "
            f"contradiction={contradiction_score:.3f}, "
            f"hallucinated={is_hallucinated}"
        )
        
        return {
            'is_hallucinated': is_hallucinated,
            'contradiction_score': float(contradiction_score),
            'confidence': 1 - contradiction_score,  # High confidence = low contradiction
            'reasoning': (
                "Response contradicts context" if is_hallucinated 
                else "Response consistent with context"
            )
        }

# Test
if __name__ == "__main__":
    detector = HallucinationDetector()
    
    # Test 1: Hallucination
    context = "Project X is complete"
    response = "Project X is still ongoing"
    result = detector.detect(response, context)
    print(f"Test 1 (hallucination): {result}")
    
    # Test 2: Consistent
    context = "Project X is complete"
    response = "Project X has finished"
    result = detector.detect(response, context)
    print(f"Test 2 (consistent): {result}")