from typing import List
import logging

logger = logging.getLogger(__name__)

class QueryExpander:
    """Generate query variations to improve recall"""
    
    def __init__(self):
        """Initialize query expander"""
        self.max_variations = 4
    
    def expand(self, query: str) -> List[str]:
        """
        Generate query variations for broader retrieval
        
        Args:
            query: Original user query
        
        Returns:
            List of query variations (original + 2-3 variations)
        """
        variations = [query]  # Always include original
        
        # Variation 1: Add context words for projects/implementations
        if any(word in query.lower() for word in ['project', 'task', 'work']):
            expanded = query + " status implementation progress"
            variations.append(expanded)
        
        # Variation 2: Add context words for discussions/updates
        if any(word in query.lower() for word in ['discuss', 'talk', 'about']):
            expanded = query.replace('discuss', 'discuss').replace('talk', 'mentioned')
            variations.append(expanded)
        
        # Variation 3: Remove question words (what, how, when, why)
        cleaned = query
        for word in ['What', 'what', 'How', 'how', 'When', 'when', 'Why', 'why', 'Is', 'is']:
            cleaned = cleaned.replace(word, '').strip()
        
        if cleaned and cleaned != query:
            variations.append(cleaned)
        
        # Variation 4: Add synonyms for common technical terms
        synonym_map = {
            'bug': 'issue error problem',
            'feature': 'functionality capability',
            'deploy': 'release launch ship',
            'update': 'change modify upgrade',
        }
        
        for key, synonyms in synonym_map.items():
            if key in query.lower():
                for synonym in synonyms.split():
                    expanded = query.replace(key, synonym)
                    if expanded not in variations:
                        variations.append(expanded)
                        break
        
        # Return up to max_variations
        return variations[:self.max_variations]

# Unit test
if __name__ == "__main__":
    expander = QueryExpander()
    
    test_queries = [
        "What is the status of project X?",
        "Tell me about the implementation details",
        "How is the budget looking?",
    ]
    
    for query in test_queries:
        expanded = expander.expand(query)
        print(f"\nOriginal: {query}")
        print(f"Variations ({len(expanded)} total):")
        for var in expanded:
            print(f"  - {var}")