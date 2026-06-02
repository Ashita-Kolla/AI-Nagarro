# Trixie AI - Employee Wellness Support Assistant

A Week 3 Agentic AI demo built with Python, FastAPI, LangGraph, TinyLlama-1.1B-Chat — now extended with **MCP-style tool integrations**.

Trixie accepts a free-text description of how an employee feels (or a quick form check-in), routes it through a 3-agent sequential pipeline, and enriches the response by calling structured **wellness tools** — demonstrating the core concepts behind the Model Context Protocol (MCP).

---

## What This Demonstrates

| Concept | Implementation |
|---------|----------------|5
| AI Agent design | 3 agents with distinct roles and prompts |
| Multi-agent workflows | LangGraph StateGraph orchestration |
| LLM prompt engineering | TinyLlama-1.1B with structured JSON prompts |
| Contextual reasoning | Context Agent extracts root cause from emotion |
| Autonomous pipeline | Input → Agent 1 → Agent 2 → Agent 3 → Output |
| **MCP Tool Integration** | **Agent decides which tools to call, invokes them, and uses results** |
| **Tool Discovery** | **`tool_registry.py` acts as a manifest (like MCP `tools/list`)** |
| **Structured Tool Results** | **Each tool returns typed JSON consumed by the agent** |

---

## Architecture

```
User Input
       │
       ▼
┌──────────────────────┐
│  Agent 1             │  Detects emotion (stressed / tired / anxious …)
│  Emotion Analyzer    │  and severity (low / medium / high)
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│  Agent 2             │  Identifies root cause:
│  Context Analyzer    │  workload / meetings / personal / unclear
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│  Agent 3             │  Selects & calls MCP-style tools,
│  Recommendation      │  then blends tool results with LLM output
└──────────┬───────────┘
     ┌─────┴──────────────────────────────────┐
     │         MCP Tool Layer                 │
     │  ┌───────────────────────────────────┐ │
     │  │ get_breathing_exercise(severity)  │ │  → Guided breathwork routine
     │  │ lookup_wellness_resources(cause)  │ │  → Curated strategies & actions
     │  │ get_stress_tip(cause, emotion)    │ │  → Motivational insight
     │  └───────────────────────────────────┘ │
     └────────────────────────────────────────┘
           ▼
     Final Response
     (rendered with visible MCP Tool Call panel)
```

Orchestrated by **LangGraph StateGraph** — a shared `WellnessState` TypedDict flows through each node, with agents reading their inputs and writing only their own outputs. `tools_used` and `tool_results` are now part of this state.

---

## How MCP Concepts Map to This Project

| MCP Concept | This Project's Equivalent |
|-------------|--------------------------|
| **MCP Server** | `tools/wellness_tools.py` — hosts the callable tool functions |
| **Tool Manifest (`tools/list`)** | `tools/tool_registry.py` → `TOOL_MANIFEST` list |
| **Tool Call (`tools/call`)** | `tool_registry.call_tool(name, **kwargs)` |
| **Tool Selection by Agent** | `tool_registry.select_tools_for(cause, severity)` |
| **Structured Tool Result** | Each tool returns a typed `dict` consumed by the agent |
| **Tool Result in Response** | `tool_results` field flows through pipeline, rendered in UI |

---

## Project Structure

```
trixie_wellness/
├── app.py                          # FastAPI backend entry point
├── requirements.txt
├── README.md
│
├── static/
│   └── index.html                  # Premium HTML/CSS/JS frontend UI
│                                   # (includes MCP Tool Call panel)
│
├── llm/
│   └── tinyllama.py                # TinyLlama singleton wrapper
│
├── agents/
│   ├── emotion_agent.py            # Agent 1: Emotion Analyzer
│   ├── context_agent.py            # Agent 2: Context Understanding
│   └── recommendation_agent.py    # Agent 3: Calls tools → blends with LLM
│
├── tools/                          # ← NEW: MCP-style tool layer
│   ├── __init__.py
│   ├── wellness_tools.py           # 3 tool functions (the "MCP server")
│   └── tool_registry.py           # Tool manifest + call_tool + select_tools_for
│
└── graph/
    └── workflow.py                 # LangGraph StateGraph + WellnessState
```

---

## Setup & Run

### 1. Create and activate a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

> Note: torch installation may take a few minutes. If you have a CUDA GPU, install the CUDA-enabled build from pytorch.org for faster inference.

### 3. Run the app locally

```bash
# From inside the trixie_wellness/ directory:
python app.py
```

Open in your browser: **http://127.0.0.1:8000**

First run: TinyLlama-1.1B-Chat-v1.0 (~2.2 GB) downloads automatically from HuggingFace and is cached locally. Takes 1–5 minutes. Subsequent runs load in ~10–30 seconds.

### 4. Run with Docker (Optional)

You can run the entire application inside a Docker container. Ensure Docker is installed and running, then execute:

```bash
# Build the Docker image
docker build -t trixie-wellness .

# Run the container
docker run -p 8000:8000 --env-file .env trixie-wellness
```

Open in your browser: **http://localhost:8000**

*Note: You can copy `.env.example` to `.env` to customize environment variables before running.*

### 5. Deploy to Render (Recommended)

This project includes a `render.yaml` Blueprint to quickly deploy to [Render](https://render.com).

1. Push your repository to GitHub/GitLab.
2. Log in to Render and go to the **Blueprints** tab.
3. Click **New Blueprint Instance** and connect your repository.
4. Render will automatically read `render.yaml` and configure the application.
5. *(Optional)* If you upgrade your service from `free` to `starter`, you can uncomment the disk configuration in `render.yaml` to ensure your SQLite DB persists between deployments!

---

## Usage

**Mode 1 — Free text:**  
Type how you feel, e.g. *"I'm stressed from back-to-back meetings and can't focus on my actual work."*

**Mode 2 — Quick form:**  
Select a stress level (Low / Medium / High) and optionally add a short note.

Click **Get Wellness Support** and watch the 3-agent pipeline run. After results appear, expand the **MCP Tool Calls** panel to inspect which tools the agent invoked and what structured data each returned.

---

## MCP Tool Details

### `get_breathing_exercise(severity)`
Returns a step-by-step guided breathing exercise matched to the user's stress severity:
- `low` → Mindful Belly Breathing (2 min)
- `medium` → Box Breathing (5 min)
- `high` → 4-7-8 Calming Breath (3 min)

### `lookup_wellness_resources(cause)`
Returns a curated list of techniques, habits, and strategies matched to the root stress cause:
- `workload` → Eat the Frog, Pomodoro, Weekly Review
- `meetings` → No-Meeting Block, 3-Bullet Agenda, Async-First
- `personal` → 5-Minute Journal, Walking Break, EAP
- `unclear` → Body Scan, Stress Audit

### `get_stress_tip(cause, emotion)`
Returns a single motivational insight tailored to cause + emotion. Used for high-severity stress or when the cause is unclear.

### Agent Tool Selection Logic (`select_tools_for`)
```
Always:   get_breathing_exercise        ← immediate relief for any check-in
If clear cause: lookup_wellness_resources ← longer-term strategies
If high severity OR unclear: get_stress_tip ← motivational nudge
```

---

## Key Design Decisions

- **TinyLlama over GPT-4**: Runs 100% locally, no API key, no cost — ideal for a demo.
- **JSON-in-prompt structured output**: 3-layer fallback (JSON parse → regex → keyword rules) ensures reliable parsing even if the model deviates.
- **Tool results take priority over LLM**: Tool-sourced recommendations fill the first slots; LLM output fills remaining slots up to 3.
- **LangGraph StateGraph**: `WellnessState` is the shared data object. `tools_used` and `tool_results` are first-class state fields — not afterthoughts.
- **MCP concepts without MCP dependency**: The tool pattern (manifest, discovery, structured call, typed result) demonstrates MCP ideas with zero extra libraries.

---

## Agent Details

### Agent 1 — Emotion Analyzer (`emotion_agent.py`)
- **Input**: raw user text + optional form stress level  
- **Output**: `emotion` (stressed / tired / anxious / overwhelmed / neutral / happy), `severity` (low / medium / high)
- **Method**: TinyLlama JSON prompt + keyword fallback

### Agent 2 — Context Analyzer (`context_agent.py`)
- **Input**: user text, emotion, severity  
- **Output**: `cause` (workload / meetings / personal / unclear), `cause_summary` (one sentence)
- **Method**: TinyLlama JSON prompt + keyword fallback

### Agent 3 — Recommendation Agent (`recommendation_agent.py`)
- **Input**: emotion, severity, cause, cause_summary  
- **Output**: `recommendations` (list of tips), `tools_used` (list of tool names), `tool_results` (raw tool data)
- **Method**: MCP-style tool selection + invocation → blended with TinyLlama generation

---

*Week 3 — Agentic AI & Multi-Agent Systems | Nagarro AI Training*
