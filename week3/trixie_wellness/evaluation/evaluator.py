import sys
import os
import json
import re

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm.tinyllama import chat

def _parse_score(llm_output: str) -> int:
    """Extracts an integer score (1-5) from LLM output."""
    match = re.search(r'\"score\"\s*:\s*(\d)', llm_output)
    if match:
        try:
            score = int(match.group(1))
            if 1 <= score <= 5:
                return score
        except ValueError:
            pass
            
    match_fallback = re.search(r'\b([1-5])\b', llm_output)
    if match_fallback:
        try:
            score = int(match_fallback.group(1))
            if 1 <= score <= 5:
                return score
        except ValueError:
            pass
            
    return 3 # Default to 3 if parsing fails

def _run_judge(system_prompt: str, user_message: str) -> int:
    try:
        raw_output = chat(system_prompt, user_message, max_new_tokens=50, temperature=0.1)
        return _parse_score(raw_output)
    except Exception as e:
        print(f"Evaluation error: {e}")
        return 3

# --- Retrieval Quality Metrics ---

def evaluate_context_precision(query: str, retrieved_context: str) -> int:
    sys_prompt = """You are an expert evaluator. Evaluate Context Precision.
Context Precision measures whether the retrieved context contains relevant information to answer the user's query.
Score from 1 to 5, where 1 means completely irrelevant and 5 means highly precise and relevant.
Respond with ONLY JSON: {"score": <int>}"""
    msg = f"Query: {query}\n\nContext: {retrieved_context}"
    return _run_judge(sys_prompt, msg)

def evaluate_context_recall(query: str, retrieved_context: str, expected_theme: str) -> int:
    sys_prompt = """You are an expert evaluator. Evaluate Context Recall.
Context Recall measures whether the retrieved context contains the expected knowledge to address the expected theme.
Score from 1 to 5, where 1 means missing completely and 5 means fully present.
Respond with ONLY JSON: {"score": <int>}"""
    msg = f"Query: {query}\nExpected Theme: {expected_theme}\n\nRetrieved Context: {retrieved_context}"
    return _run_judge(sys_prompt, msg)

def evaluate_faithfulness(retrieved_context: str, response: str) -> int:
    sys_prompt = """You are an expert evaluator. Evaluate Faithfulness.
Faithfulness measures whether the response is derived from the provided context without hallucinating outside facts.
Score from 1 to 5, where 1 means entirely hallucinated and 5 means perfectly faithful to the context.
Respond with ONLY JSON: {"score": <int>}"""
    msg = f"Context: {retrieved_context}\n\nResponse: {response}"
    return _run_judge(sys_prompt, msg)

# --- Response Quality Metrics ---

def evaluate_relevance(query: str, response: str) -> int:
    sys_prompt = """You are an expert evaluator. Evaluate Relevance.
Relevance measures how well the response directly answers or addresses the user's query.
Score from 1 to 5, where 1 means totally irrelevant and 5 means perfectly relevant.
Respond with ONLY JSON: {"score": <int>}"""
    msg = f"Query: {query}\n\nResponse: {response}"
    return _run_judge(sys_prompt, msg)

def evaluate_helpfulness(query: str, response: str) -> int:
    sys_prompt = """You are an expert evaluator. Evaluate Helpfulness.
Helpfulness measures whether the response is empathetic, actionable, and supportive for a wellness application.
Score from 1 to 5, where 1 means unhelpful/rude and 5 means highly helpful and supportive.
Respond with ONLY JSON: {"score": <int>}"""
    msg = f"Query: {query}\n\nResponse: {response}"
    return _run_judge(sys_prompt, msg)

def evaluate_groundedness(response: str) -> int:
    sys_prompt = """You are an expert evaluator. Evaluate Groundedness.
Groundedness measures whether the response relies on factual, logical statements without unsupported medical claims.
Score from 1 to 5, where 1 means ungrounded/dangerous claims and 5 means safe and well-grounded.
Respond with ONLY JSON: {"score": <int>}"""
    msg = f"Response: {response}"
    return _run_judge(sys_prompt, msg)
