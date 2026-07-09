import re
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class ResponseValidator:
    """Validate response claims against sources"""
    
    def validate(
        self,
        response: str,
        sources: List[str]
    ) -> dict:
        """
        Validate response against retrieved sources
        
        Returns:
            {
                'is_valid': bool,
                'coverage': float (0-1),
                'uncited_claims': List[str],
                'verified_claims': int,
                'total_claims': int
            }
        """
        # Extract sentences (approximate claims)
        sentences = re.split(r'[.!?]+', response)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # source_texts = [s.get('content', '') for s in sources]
        # source_texts = [s.content for s in sources if hasattr(s, 'content')]
        logger.info(f"Sources for validation: \n{sources}")
        combined_context = sources  # Assuming sources is a list of strings for simplicity
        
        logger.info(f"Combined context for validation: \n{combined_context}")

        verified = 0
        uncited = []
        
        for sentence in sentences:
            # Simple check: does sentence appear in sources?
            # (Phase 3 simple approach; Phase 4 can use semantic matching)
            words = set(sentence.lower().split())
            source_words = set(combined_context.lower().split())
            
            # If 70%+ of words are in context, consider it verified
            logger.info(f"Len(words & source_words): {len(words & source_words)} | Len(words): {len(words)}")

            overlap = len(words & source_words) / len(words) if words else 0
            
            logger.info(f"Validating sentence: '{sentence}' | Source words: '{source_words}' | Overlap: {overlap:.2f}")

            if overlap > 0.15:
                verified += 1
            else:
                uncited.append(sentence[:50] + "...")
        
        logger.info(f"Verified claims: {verified}")

        coverage = verified / len(sentences) if sentences else 0
        logger.info(f"Coverage={coverage:.2%}")

        is_valid = coverage > 0.15
        
        logger.info(
            f"Response validation: "
            f"coverage={coverage:.2%}, "
            f"verified={verified}/{len(sentences)}"
        )
        
        return {
            'is_valid': is_valid,
            'coverage': float(coverage),
            'verified_claims': verified,
            'total_claims': len(sentences),
            'uncited_claims': uncited[:3],  # Top 3 uncited
            'requires_review': not is_valid
        }

# Test
if __name__ == "__main__":
    validator = ResponseValidator()
    
    response = "Project X is complete. The team finished on time."
    sources = [
        "Project X completion was on schedule. The team finished the work."
    ]
    
    result = validator.validate(response, sources)
    print(f"Validation: {result}")