import asyncio
from backend.app.api.routes import chat
from backend.app.models.schemas import ChatQuery

async def test():
    queries = [
        "What is the main topic?",
        "Tell me about project X",
        "What was the budget?",
    ]
    
    for query_text in queries:
        query = ChatQuery(text=query_text, top_k=5)
        response = await chat(query)
        
        print(f"\nQuery: {query_text}")
        print(f"  Answer: {response.answer[:80]}...")
        print(f"  Hallucination detected: {response.hallucination_detected}")
        print(f"  Validation coverage: {response.validation_coverage:.0%}")
        print(f"  Fallback used: {response.fallback_used}")

asyncio.run(test())
