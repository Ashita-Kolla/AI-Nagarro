import importlib
import json
from .hitl import human_gate

class AgentRunner:
    def __init__(self, context_manager, supervisor):
        self.context_manager = context_manager
        self.supervisor = supervisor
        
    def run_queue(self, execution_queue, start_index=0):
        """
        Executes each agent in the queue, handling quality checks and HITL.
        """
        for i in range(start_index, len(execution_queue)):
            agent_name = execution_queue[i]
            print(f"\n{'='*50}\nExecuting {agent_name}...\n{'='*50}")
            
            # Dynamically import the agent module
            try:
                module_name = f"agents.{agent_name.lower()}"
                agent_module = importlib.import_module(module_name)
            except ImportError as e:
                print(f"Error loading agent module for {agent_name}: {e}")
                return
                
            human_note = None
            
            while True:
                # Call the agent's run function
                result_data = agent_module.run(self.context_manager, correction=human_note)
                
                if not result_data:
                    print(f"Failed to get valid output from {agent_name}. Quitting.")
                    return
                    
                print(f"\n--- Output for {agent_name} ---\n")
                print(json.dumps(result_data, indent=2, ensure_ascii=False))
                print("\n-------------------------------\n")
                
                # Quality Check
                self.supervisor.check_quality(agent_name, result_data, self.context_manager)
                
                # Human Gate
                action, correction = human_gate(agent_name)
                
                if action == 'A':
                    self.context_manager.add_output(agent_name, result_data)
                    print(f"Step {agent_name} approved and context saved.")
                    break
                elif action == 'E':
                    human_note = human_note + f"\n- {correction}" if human_note else correction
                    print(f"Applying correction and rerunning {agent_name}...")
                elif action == 'R':
                    print("Regenerating...")
                elif action == 'Q':
                    print("Quitting. Progress up to the previous step is saved.")
                    return
        
        print("\nAll steps completed successfully!")
