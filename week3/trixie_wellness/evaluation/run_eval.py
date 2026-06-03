import sys
import os
import json
import csv
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph.workflow import run_pipeline
from evaluation.evaluator import (
    evaluate_context_precision,
    evaluate_context_recall,
    evaluate_faithfulness,
    evaluate_relevance,
    evaluate_helpfulness,
    evaluate_groundedness
)

DATASET_PATH = os.path.join(os.path.dirname(__file__), "dataset.json")
RESULTS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "evaluation_results.csv")

def run_evaluation_batch():
    print("Starting LLM Evaluation Batch...")
    with open(DATASET_PATH, "r") as f:
        dataset = json.load(f)
        
    results = []
    
    for item in dataset:
        q_id = item["id"]
        query = item["user_input"]
        expected_theme = item.get("expected_theme", "")
        
        print(f"Evaluating Q{q_id}: {query}")
        
        # 1. Run Pipeline
        try:
            state = run_pipeline(query)
            context = state.get("rag_context", "")
            
            if state.get("is_flagged"):
                response = state.get("safety_response", "")
            else:
                recs = state.get("recommendations", [])
                response = " ".join([str(r) for r in recs])
                
            # 2. Compute Metrics
            ctx_precision = evaluate_context_precision(query, context)
            ctx_recall = evaluate_context_recall(query, context, expected_theme)
            faithfulness = evaluate_faithfulness(context, response)
            
            relevance = evaluate_relevance(query, response)
            helpfulness = evaluate_helpfulness(query, response)
            groundedness = evaluate_groundedness(response)
            
        except Exception as e:
            print(f"Error during pipeline execution for Q{q_id}: {e}")
            ctx_precision, ctx_recall, faithfulness = 0, 0, 0
            relevance, helpfulness, groundedness = 0, 0, 0
            
        result_row = {
            "timestamp": datetime.now().isoformat(),
            "query_id": q_id,
            "user_input": query,
            "context_precision": ctx_precision,
            "context_recall": ctx_recall,
            "faithfulness": faithfulness,
            "relevance": relevance,
            "helpfulness": helpfulness,
            "groundedness": groundedness
        }
        results.append(result_row)
        
    # 3. Write to CSV
    file_exists = os.path.isfile(RESULTS_PATH)
    fieldnames = [
        "timestamp", "query_id", "user_input", 
        "context_precision", "context_recall", "faithfulness", 
        "relevance", "helpfulness", "groundedness"
    ]
    
    with open(RESULTS_PATH, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerows(results)
        
    print(f"Evaluation complete. Results saved to {RESULTS_PATH}")
    return results

if __name__ == "__main__":
    run_evaluation_batch()
