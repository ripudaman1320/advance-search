from backend.app.generation.response_builder import ResponseBuilder

builder = ResponseBuilder()

response = """
Project X is on track [Source: Sarah | 2024-06-15].
The team completed 85% [Source: John | 2024-06-10].
"""

sources = [
    {'sender': 'Sarah', 'source_doc_id': 'email_1', 'confidence': 0.9},
    {'sender': 'John', 'source_doc_id': 'email_2', 'confidence': 0.85},
]

built = builder.build(response, sources)

print("Built response:")
print(f"  Citations: {len(built['citations'])}")
print(f"  Coverage: {built.get('citation_coverage', 0):.0f}%")

print("\nFormatted for UI:")
formatted = builder.format_for_ui(built)
print(formatted)
