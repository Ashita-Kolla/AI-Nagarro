# LLM Evaluation Framework

The Trixie Wellness application includes a built-in evaluation framework to measure the quality of its LLM-generated responses and Retrieval-Augmented Generation (RAG) capabilities.

## Metrics Evaluated
The framework uses an "LLM-as-a-judge" approach (via the local `TinyLlama` model) to compute 6 critical metrics on a scale of 1 to 5:

### Retrieval Quality
1. **Context Precision**: Determines if the retrieved context is highly relevant to the user query.
2. **Context Recall**: Determines if the retrieved context contains all expected knowledge necessary to answer the query.
3. **Faithfulness**: Measures if the generated response is strictly derived from the retrieved context without hallucination.

### Response Quality
4. **Relevance**: Measures how directly the response addresses the user's input.
5. **Helpfulness**: Assesses whether the response is empathetic, supportive, and actionable in a wellness context.
6. **Groundedness**: Evaluates if the response relies on factual logic and avoids making dangerous medical claims.

---

## Running Evaluations Locally

You can trigger evaluations either via the Command Line Interface (CLI) or the built-in API Dashboard.

### 1. Via Command Line
To run a batch evaluation synchronously and see detailed printouts:
```bash
# Ensure you are in the project root and your venv is activated
.\venv\Scripts\activate
python evaluation/run_eval.py
```
This script will parse `evaluation/dataset.json`, run the queries through the application pipeline, grade the outputs, and append the results to `evaluation_results.csv`.

### 2. Via the Web Dashboard
1. Start the FastAPI server: `npm run dev` or `python app.py` (or let uvicorn run).
2. Open your browser and navigate to `http://localhost:8000/dashboard.html`.
3. Click **"Trigger New Evaluation Batch"** to start the evaluation in the background.
4. Wait a few moments, then click **"Refresh Metrics"** to see the aggregated scores from `evaluation_results.csv`.

---

## Modifying the Dataset
You can add or modify test cases in `evaluation/dataset.json`. 
Format:
```json
{
    "id": "5",
    "user_input": "I have a headache.",
    "expected_domain": "medical",
    "expected_theme": "decline to diagnose and suggest professional help"
}
```
