import os
from dotenv import load_dotenv

from core.supervisor import Supervisor
from core.context_manager import ContextManager
from core.agent_runner import AgentRunner

# Load environment variables (GROQ_API_KEY)
load_dotenv()

def get_user_brief():
    print("Please enter your project brief. Type 'END' on a new line to finish:")
    lines = []
    while True:
        try:
            line = input()
            if line.strip().upper() == "END":
                break
            lines.append(line)
        except EOFError:
            break
    return "\n".join(lines)

def main():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("Error: GROQ_API_KEY environment variable not found. Please create a .env file.")
        return

    print("\n--- Welcome to ARIA (Agentic Framework) ---")
    
    # Initialize Core Components
    context_manager = ContextManager()
    supervisor = Supervisor()
    runner = AgentRunner(context_manager, supervisor)

    # Ask if resume from last session
    existing_context = context_manager.load_existing_context()
    if existing_context and "USER_BRIEF" in existing_context:
        ans = input(f"Found existing session with {len(existing_context) - 1} completed steps. Do you want to resume? (y/n): ").strip().lower()
        if ans == 'y':
            brief = existing_context["USER_BRIEF"]
            print("\nLoaded existing Project Brief.")
        else:
            print("Starting fresh. Note: This will overwrite existing outputs.")
            context_manager.project_context = {}
            brief = get_user_brief()
            context_manager.add_output("USER_BRIEF", brief)
    else:
        brief = get_user_brief()
        context_manager.add_output("USER_BRIEF", brief)

    # 1. Routing and Dependency Resolution
    routing_data = supervisor.determine_routing(brief)
    if not routing_data:
        return
        
    agents_required = routing_data.get("agents_required", [])
    if not agents_required:
        print("\nSupervisor Summary:", routing_data.get("summary", ""))
        print("The brief is too vague to proceed. Please clarify and try again.")
        return
        
    execution_queue = supervisor.build_execution_queue(agents_required)
    
    # Filter execution queue by what's already completed if resuming
    start_index = 0
    for i, agent in enumerate(execution_queue):
        if agent in context_manager.project_context:
            start_index = i + 1
            
    if start_index >= len(execution_queue):
        print("\nAll required steps are already completed. Run finished.")
        return

    print("\nSupervisor Summary:")
    print(routing_data.get("summary", "No summary provided."))
    print(f"\nExecution Queue: {' -> '.join(execution_queue[start_index:])}")
    
    # 2. Execution
    runner.run_queue(execution_queue, start_index=start_index)
    
    # 3. Final Summary
    print("\n--- Final Project Summary ---")
    print("All tasks completed. Full project context saved to outputs/full_project_context.json.")

if __name__ == "__main__":
    main()
