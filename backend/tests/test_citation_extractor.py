from backend.app.generation.citation_extractor import CitationExtractor
from backend.app.models.schemas import RetrievalResult

extractor = CitationExtractor()

response = """
Project X is on track with implementation [Source: Sarah | 2024-06-15].
The team has completed 85% of the work [Source: John | 2024-06-10].
Next milestone is testing phase [Source: Sarah | 2024-06-20].
"""

sources = [
    {'sender': 'Sarah', 'source_doc_id': 'email_1', 'confidence': 0.9},
    {'sender': 'John', 'source_doc_id': 'email_2', 'confidence': 0.85},
]

citations = extractor.extract(response, sources)

print(f"Found {len(citations)} citations:")
for c in citations:
    print(f"  - {c['sender']} ({c['timestamp']}): {c['verified']}")

verification = extractor.verify_citations(citations)
print(f"\nVerification: {verification}")

# Regression test for retrieval results with sender extracted from content
content_source = RetrievalResult(
    chunk_id='0707b5beff8e0586_0',
    content="""**From**: sawzank@gmail.com (Shasanka Acharya)
**Date**: 2013-12-23T23:15:00
""",
    score=0.9999943,
    confidence=0.5499976873397827,
    source_doc_id='0707b5beff8e0586',
    sender='',
    timestamp='2013-12-23T23:15:00'
)

content_response = "Email content summary [Source: sawzank@gmail.com | 2013-12-23T23:15:00]."
content_citations = extractor.extract(content_response, [content_source])
assert len(content_citations) == 1
assert content_citations[0]['verified'] is True
assert content_citations[0]['source_id'] == '0707b5beff8e0586'
