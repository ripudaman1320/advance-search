from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class FallbackHandler:
    """Handle low-confidence or hallucinated responses"""
    
    def __init__(
        self,
        hallucination_threshold: float = 0.5,
        confidence_threshold: float = 0.5,
        validation_threshold: float = 0.15
    ):
        self.hallucination_threshold = hallucination_threshold
        self.confidence_threshold = confidence_threshold
        self.validation_threshold = validation_threshold
    
    def should_fallback(
        self,
        hallucination_score: dict,
        confidence_score: float,
        validation_result: dict
    ) -> tuple[bool, str]:
        """
        Determine if we should fallback to safe response
        
        Returns: (should_fallback, reason)
        """
        # Check hallucination
        if hallucination_score.get('is_hallucinated'):
            return True, "Potential hallucination detected"
        
        # Check confidence
        if confidence_score < self.confidence_threshold:
            return True, "Low retrieval confidence"
        
        # Check validation coverage
        if validation_result.get('coverage', 0) < self.validation_threshold:
            return True, "Insufficient claim verification"
        
        return False, "Response safe"
    
    def get_fallback_response(self, reason: str) -> str:
        """Get safe fallback message based on reason"""
        fallbacks = {
            "Potential hallucination detected": (
                "I'm not confident enough in this answer. "
                "The generated response may not be fully supported by your emails. "
                "Could you rephrase your question?"
            ),
            "Low retrieval confidence": (
                "I couldn't find strong evidence in your emails for this question. "
                "Try rephrasing or asking about a different topic."
            ),
            "Insufficient claim verification": (
                "Some claims in my response aren't well-supported. "
                "I recommend reviewing the source emails directly."
            )
        }
        return fallbacks.get(reason, "I don't have enough information to answer confidently.")

# Test
if __name__ == "__main__":
    handler = FallbackHandler()
    
    halluc = {'is_hallucinated': False}
    conf = 0.7
    valid = {'coverage': 0.9}
    
    should_fall, reason = handler.should_fallback(halluc, conf, valid)
    print(f"Should fallback: {should_fall}, Reason: {reason}")
    
    # Test hallucination detection
    halluc = {'is_hallucinated': True}
    should_fall, reason = handler.should_fallback(halluc, conf, valid)
    print(f"With hallucination: {should_fall}, Reason: {reason}")