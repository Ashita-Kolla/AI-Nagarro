# ARIA (Automated Requirements and Implementation Agent)

**ARIA** is a stateful, multi-agent AI framework designed to automate the entire software development lifecycle (SDLC). By chaining together specialized Large Language Model (LLM) agents, ARIA can handle everything from business analysis and architecture design to code generation, QA testing, and DevOps planning.

The project is built with a **Python FastAPI / LangGraph backend** and a **React (Vite) frontend** connected via WebSockets to enable real-time tracking of the agent pipeline and human-in-the-loop interventions.

---

## 🌟 Key Features of this Project 

- **Multi-Agent Pipeline**: Specialized agents (BA, Architect, Planner, Developer, QA, DevOps, PM, Optimisation) working sequentially on your software brief.
- **LangGraph Orchestration**: Uses state graphs and SQLite checkpoints to seamlessly pause, resume, and manage agent states.
- **Human-in-the-Loop (HITL)**: Built-in safety gates allowing human operators to approve, edit, or regenerate agent outputs before proceeding to the next step.
- **Real-Time UI**: A React-based interface communicating with the backend over WebSockets to display live logs, diagrams, and artifact generation.

---

## 🏗️ System Architecture

1. **User Input (Brief)**: The user provides a project brief via the UI.
2. **Supervisor Routing**: The Supervisor Agent analyzes the brief, determines the project type (e.g., new application, bug fix), and constructs an execution queue.
3. **Sequential Execution**: The pipeline runs through required roles, passing a `ContextManager` state between them.
4. **Artifact Generation**: Outputs (codebases, documentation, test scripts) are persisted to the local file system in the `outputs/` directory.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Node.js (for the frontend, though a local `node/` folder is included in the start script)
- A Groq API Key (or other configured LLM provider)

### 1. Configuration

Create a `.env` file in the root of the ARIA folder and add your LLM API key:

```env
GROQ_API_KEY=your_api_key_here
```

### 2. Running the Application

You can run the application using either a unified helper script or manually in separate terminals.

#### Option A: Running with the helper script (Recommended)

You can start the frontend development server using the provided PowerShell script. (Make sure you have a separate terminal running the backend if the script only starts the frontend).

```powershell
# 1. Navigate to the ARIA folder
cd "c:\Users\ashitakolla\OneDrive - Nagarro\Desktop\AI-Nagarro\ARIA"

# 2. Run the startup script (it automatically adds the local Node folder to PATH)
.\start-dev.ps1
```

#### Option B: Running both manually in separate terminals

If you prefer to run the backend and frontend manually:

**Terminal 1: Backend**

```powershell
# 1. Navigate to ARIA folder
cd "c:\Users\ashitakolla\OneDrive - Nagarro\Desktop\AI-Nagarro\ARIA"

# 2. Start the FastAPI/uvicorn server
.\.venv\Scripts\python.exe -m uvicorn ws_server:app --port 8000  
```

**Terminal 2: Frontend**

```powershell
# 1. Navigate to the ARIA folder
cd "c:\Users\ashitakolla\OneDrive - Nagarro\Desktop\AI-Nagarro\ARIA"

# 2. Run the startup script (starts Vite server on port 5173 by default)
.\start-dev.ps1
```

---

## 📂 Project Structure

- `agents/` - Individual agent implementations (BA, Developer, QA, etc.).
- `core/` - Orchestration logic (`supervisor.py`, `langgraph_runner.py`, `context_manager.py`).
- `my-aria-app/` - React frontend application (Vite).
- `prompts/` - Markdown files containing the system prompts for each agent.
- `ws_server.py` - FastAPI WebSocket server.
- `aria.py` - Command-line interface alternative to the web UI.

---

## Acknowledgments

Developed under the mentorship of Mahim Mohan and Prashnat Srivastava.
