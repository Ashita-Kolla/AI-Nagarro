AGENT_REGISTRY = {
    "BA": {
        "name": "BA",
        "prompt_file": "step_02_ba.md",
        "requires": [],
        "description": "Business Analysis agent responsible for defining user stories and requirements."
    },
    "Architect": {
        "name": "Architect",
        "prompt_file": "step_03_architect.md",
        "requires": ["BA"],
        "description": "System Architecture agent responsible for defining the technical architecture and tech stack."
    },
    "Developer": {
        "name": "Developer",
        "prompt_file": "step_04_developer.md",
        "requires": ["Architect"],
        "description": "Development agent responsible for detailing technical implementation steps."
    },
    "QA": {
        "name": "QA",
        "prompt_file": "step_05_qa.md",
        "requires": ["Developer"],
        "description": "Quality Assurance agent responsible for creating test plans and edge cases."
    },
    "DevOps": {
        "name": "DevOps",
        "prompt_file": "step_06_devops.md",
        "requires": ["QA"],
        "description": "DevOps agent responsible for deployment, CI/CD, and infrastructure planning."
    },
    "PM": {
        "name": "PM",
        "prompt_file": "step_07_pm.md",
        "requires": ["DevOps"],
        "description": "Project Management agent responsible for timelines, sprints, and risk management."
    },
    "Optimisation": {
        "name": "Optimisation",
        "prompt_file": "step_08_optimisation.md",
        "requires": ["PM"],
        "description": "Optimisation agent responsible for reviewing the pipeline for efficiency and deduplication."
    }
}

def resolve_execution_queue(required_agents):
    """
    Takes a list of required agent names and resolves dependencies automatically
    to build an ordered execution queue.
    Uses a simple topological-like sort.
    """
    # Find all dependencies recursively
    queue_set = set(required_agents)
    
    def add_deps(agent_name):
        if agent_name not in AGENT_REGISTRY:
            return
        for dep in AGENT_REGISTRY[agent_name]["requires"]:
            if dep not in queue_set:
                queue_set.add(dep)
                add_deps(dep)
                
    for agent in required_agents:
        add_deps(agent)
        
    # Sort them according to a hardcoded standard order based on the registry
    # to guarantee a clean linear flow (BA -> Architect -> Developer -> QA -> DevOps -> PM -> Optimisation)
    # This acts as our topological sort since the flow is mostly linear.
    standard_order = ["BA", "Architect", "Developer", "QA", "DevOps", "PM", "Optimisation"]
    
    final_queue = [agent for agent in standard_order if agent in queue_set]
    return final_queue
