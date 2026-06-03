from fastapi import APIRouter, HTTPException, BackgroundTasks
import os
import csv

from evaluation.run_eval import run_evaluation_batch

router = APIRouter(prefix="/api/evaluation", tags=["evaluation"])

RESULTS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "evaluation_results.csv")

@router.post("/run")
def trigger_evaluation(background_tasks: BackgroundTasks):
    """Triggers the batch evaluation process in the background."""
    background_tasks.add_task(run_evaluation_batch)
    return {"status": "success", "message": "Evaluation batch triggered in the background."}

@router.get("/dashboard")
def get_evaluation_dashboard():
    """Reads evaluation results and returns aggregated metrics."""
    if not os.path.exists(RESULTS_PATH):
        return {"status": "success", "metrics": {}}
        
    try:
        metrics_sum = {
            "context_precision": 0,
            "context_recall": 0,
            "faithfulness": 0,
            "relevance": 0,
            "helpfulness": 0,
            "groundedness": 0
        }
        count = 0
        
        with open(RESULTS_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                count += 1
                for key in metrics_sum.keys():
                    try:
                        metrics_sum[key] += float(row.get(key, 0))
                    except ValueError:
                        pass
                        
        if count == 0:
            return {"status": "success", "metrics": {}}
            
        metrics_avg = {k: round(v / count, 2) for k, v in metrics_sum.items()}
        return {
            "status": "success",
            "total_runs": count,
            "metrics": metrics_avg
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
