from rag.router import classify_intent
from rag.vectorstore import get_rag

print("Initializing RAG vector stores...")
rag = get_rag()

queries = [
    "I am overwhelmed with all these deadlines and my boss keeps giving me tasks.",
    "I can't breathe, I'm having a panic attack right now.",
    "I just feel generally anxious and tired, and haven't slept well."
]

for q in queries:
    print(f"\n--- Query: {q} ---")
    domain = classify_intent(q)
    print(f"Classified Domain: {domain}")
    context = rag.retrieve(domain, q, k=1)
    print(f"Retrieved Context Snippet: {context[:100]}...")
