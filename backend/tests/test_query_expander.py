from backend.app.retrieval.query_expander import QueryExpander

expander = QueryExpander()

test_queries = [
    "What is the status of project X?",
    "Tell me about the implementation",
    "How is the budget?",
    "What bugs were reported?",
    "Discuss the timeline",
]

for query in test_queries:
    expanded = expander.expand(query)
    print(f"\nOriginal: {query}")
    print(f"Variations ({len(expanded)} total):")
    for i, var in enumerate(expanded, 1):
        print(f"  {i}. {var}")
