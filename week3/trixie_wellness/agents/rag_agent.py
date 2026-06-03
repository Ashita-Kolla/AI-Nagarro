from rag.router import classify_intent
from rag.vectorstore import get_rag

def run_rag_agent(state: dict) -> dict:
    """
    RAG Agent node in the workflow.
    It takes the user input, classifies the intent to find the domain,
    retrieves context from the vector store, and adds it to the state.
    """
    user_input = state.get("user_input", "")
    
    # 1. Classify intent to get the appropriate domain
    domain = classify_intent(user_input)
    
    # 2. Retrieve relevant context from the selected vector store
    rag = get_rag()
    context = rag.retrieve(domain, user_input, k=2)
    
    # Return updates to the state
    return {
        "rag_domain": domain,
        "rag_context": context
    }
