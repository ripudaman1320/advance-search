from typing import List, Dict
from app.generation.citation_extractor import CitationExtractor

class ResponseBuilder:
    """Build formatted responses with citations"""
    
    def __init__(self):
        self.citation_extractor = CitationExtractor()
    
    def build(self, answer: str, sources: List[Dict], include_citations: bool = True) -> Dict:
        """
        Build formatted response with citations
        
        Args:
            answer: Generated answer from LLM
            sources: List of retrieved source metadata
            include_citations: Whether to extract and include citations
        
        Returns:
            Dictionary with formatted response
        """
        result = {
            "answer": answer,
            "sources": sources,
            "citations": []
        }
        
        if include_citations:
            citations = self.citation_extractor.extract(answer, sources)
            result["citations"] = citations
            
            # Mark whether response has good citation coverage
            if len(citations) > 0:
                coverage = len(citations) / max(len(answer.split()), 1) * 100
                result["citation_coverage"] = coverage
        
        return result
    
    def format_for_ui(self, response: Dict) -> str:
        """Format response for display in UI"""
        formatted = response["answer"]
        
        # Add citation indicators
        for citation in response.get("citations", []):
            marker = citation["marker"]
            indicator = f" [✓ {citation['sender']}]" if citation["verified"] else f" [? {citation['sender']}]"
            formatted = formatted.replace(marker, marker + indicator)
        
        return formatted
