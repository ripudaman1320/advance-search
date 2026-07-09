import re
from typing import Any, List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class CitationExtractor:
    """Extract and verify citations from LLM responses"""
    
    def __init__(self):
        """Initialize citation extractor"""
        # Pattern to match [Source: sender | timestamp] markers
        self.citation_pattern = r'\[Source:\s*(.+?)\s*\|\s*(.+?)\]'
        self.sender_pattern = r'\bfrom\s+(\w+(?:\s+\w+)*?)\b'

    def _get_source_field(self, source: Any, field: str, default: str = '') -> str:
        if isinstance(source, dict):
            return source.get(field, default) or default
        return getattr(source, field, default) or default

    def _parse_sender_from_content(self, content: str) -> str:
        if not content:
            return ''

        patterns = [
            r'\*\*From\*\*:\s*(?P<email>[^\s(]+)(?:\s*\((?P<name>[^)]+)\))?',
            r'^From:\s*(?P<email>[^\s(]+)(?:\s*\((?P<name>[^)]+)\))?',
        ]

        for pattern in patterns:
            match = re.search(pattern, content, flags=re.IGNORECASE | re.MULTILINE)
            if match:
                return (match.group('email') or match.group('name') or '').strip()

        return ''
    
    def extract(
        self,
        response: str,
        retrieved_sources: List[Dict]
    ) -> List[Dict]:
        """
        Extract citations from response text
        
        Args:
            response: Generated response text from LLM
            retrieved_sources: List of source metadata from retrieval
        
        Returns:
            List of citations with verified sources
        """
        citations = []
        
        # Find all [Source: ...] markers
        matches = list(re.finditer(self.citation_pattern, response))
        logger.info(f"Found {len(matches)} citation markers in response")
        
        for match in matches:
            sender = match.group(1).strip()
            timestamp = match.group(2).strip()
            
            # Find matching source
            matching_source = None
            for source in retrieved_sources:
                logger.info(f"Checking source: {source}")
                source_sender = self._get_source_field(source, 'sender')
                if not source_sender:
                    source_content = self._get_source_field(source, 'content')
                    source_sender = self._parse_sender_from_content(source_content)

                if source_sender and source_sender.lower() == sender.lower():
                    matching_source = source
                    break
            
            if matching_source:
                source_id = self._get_source_field(matching_source, 'source_doc_id')
                confidence = self._get_source_field(matching_source, 'confidence', 0.0)
                citation = {
                    'marker': match.group(0),  # Full [Source: ...] text
                    'sender': sender,
                    'timestamp': timestamp,
                    'source_id': source_id,
                    'verified': True,
                    'confidence': confidence
                }
                citations.append(citation)
                logger.debug(f"Verified citation: {sender} | {timestamp}")
            else:
                # Source not found
                citation = {
                    'marker': match.group(0),
                    'sender': sender,
                    'timestamp': timestamp,
                    'source_id': None,
                    'verified': False,
                    'confidence': 0.0
                }
                citations.append(citation)
                logger.warning(f"Unverified citation: {sender}")
        
        return citations
    
    def extract_with_context(
        self,
        response: str,
        retrieved_sources: List[Dict]
    ) -> List[Dict]:
        """
        Extract citations with surrounding context
        
        Args:
            response: Generated response
            retrieved_sources: Source metadata
        
        Returns:
            List of citations with context snippets
        """
        citations = self.extract(response, retrieved_sources)
        
        # Add context around each citation
        for citation in citations:
            marker = citation['marker']
            if marker in response:
                pos = response.find(marker)
                start = max(0, pos - 50)
                end = min(len(response), pos + len(marker) + 50)
                context = response[start:end].strip()
                citation['context'] = context
        
        return citations
    
    def verify_citations(
        self,
        citations: List[Dict],
        confidence_threshold: float = 0.5
    ) -> Dict:
        """
        Verify citation accuracy and quality
        
        Args:
            citations: List of extracted citations
            confidence_threshold: Minimum confidence to mark as verified
        
        Returns:
            Dictionary with verification results
        """
        verified_count = sum(1 for c in citations if c.get('verified'))
        high_confidence_count = sum(
            1 for c in citations 
            if c.get('confidence', 0) >= confidence_threshold
        )
        
        return {
            'total_citations': len(citations),
            'verified': verified_count,
            'high_confidence': high_confidence_count,
            'verification_rate': verified_count / len(citations) if citations else 0,
            'confidence_rate': high_confidence_count / len(citations) if citations else 0
        }