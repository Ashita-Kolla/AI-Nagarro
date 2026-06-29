import os
import json
import subprocess
from core.llm_utils import call_llm, parse_json_from_llm
from core.context_compressor import compress_context_for_agent

def build_prompt(context_manager, correction: str = None) -> str:
    raw_context = context_manager.get_context()
    context = compress_context_for_agent("Environment", raw_context)
    
    user_brief = context.get("USER_BRIEF", "")
    architect_output = context.get("Architect", {})
    developer_output = context.get("Developer", {})

    prompt_path = os.path.join("prompts", "step_04b_environment.md")
    with open(prompt_path, "r", encoding="utf-8") as f:
        template = f.read()

    prompt = template.replace("{USER_BRIEF}", user_brief)
    prompt = prompt.replace("{ARCHITECT_OUTPUT}", str(architect_output)[:1500])
    prompt = prompt.replace("{DEVELOPER_OUTPUT}", str(developer_output)[:1500])

    if correction:
        prompt += f"\n\n=== HUMAN CORRECTION ===\nPlease apply the following corrections:\n{correction}\n"

    return prompt

def execute_setup_script(setup_script_name: str, commands: list) -> dict:
    """
    Writes the setup script to the target folder and executes it.
    """
    qa_dir = os.path.join("outputs", "QA", "tests")
    os.makedirs(qa_dir, exist_ok=True)
    
    script_path = os.path.join(qa_dir, setup_script_name)
    
    # Write the script
    with open(script_path, "w", encoding="utf-8") as f:
        for cmd in commands:
            f.write(cmd + "\n")
            
    print(f"Environment Agent: Executing setup script {setup_script_name} locally...")
    try:
        # Determine how to run based on extension
        if setup_script_name.endswith(".ps1"):
            cmd_runner = ["powershell", "-ExecutionPolicy", "Bypass", "-File", setup_script_name]
        elif setup_script_name.endswith(".sh"):
            cmd_runner = ["bash", setup_script_name]
        else:
            # Fallback to run commands one by one
            cmd_runner = None
            
        if cmd_runner:
            result = subprocess.run(
                cmd_runner, 
                cwd=qa_dir, 
                capture_output=True, 
                text=True, 
                timeout=120
            )
            passed = (result.returncode == 0)
            log_output = result.stdout + "\n" + result.stderr
        else:
            # Run sequentially
            passed = True
            log_output = ""
            for cmd in commands:
                result = subprocess.run(
                    cmd, 
                    shell=True,
                    cwd=qa_dir, 
                    capture_output=True, 
                    text=True, 
                    timeout=120
                )
                log_output += f"> {cmd}\n{result.stdout}\n{result.stderr}\n"
                if result.returncode != 0:
                    passed = False
                    break
                    
        return {
            "status": "PASS" if passed else "FAIL",
            "log": log_output
        }
    except Exception as e:
        return {
            "status": "FAIL",
            "log": f"Execution Environment Error: {str(e)}"
        }

def run(context_manager, correction: str = None) -> dict:
    try:
        prompt = build_prompt(context_manager, correction)
        response_text = call_llm(prompt, agent_name="Environment")
        parsed_data = parse_json_from_llm(response_text)

        if not parsed_data:
            print("Environment Agent Error: Failed to parse valid JSON from LLM.")
            return {}

        # Extract commands but do NOT execute automatically
        setup_commands = parsed_data.get("setup_commands", [])
        
        if setup_commands:
            parsed_data["execution_status"] = "PENDING_APPROVAL"
            parsed_data["execution_log"] = "Waiting for human test run or approval."
        
        return parsed_data
    except Exception as e:
        print(f"Environment Agent Error: {str(e)}")
        return {}

def post_approval(data: dict, context_manager) -> list:
    """
    Exports the Environment artifacts.
    Also checks if the human saved an edited script to disk, and injects it into context.
    """
    out_dir = os.path.join("outputs", "Environment")
    os.makedirs(out_dir, exist_ok=True)
    
    generated_files = []

    # Inject edited script if available
    edited_script_path = os.path.join(out_dir, "setup.ps1")
    if os.path.exists(edited_script_path):
        with open(edited_script_path, "r", encoding="utf-8") as f:
            script_content = f.read()
        data["setup_commands"] = script_content.split('\n')
        # Update context manager so downstream agents get the edited script
        context_manager.add_output("Environment", data)
        generated_files.append(edited_script_path)
    else:
        # If no edit was made, write the LLM's original script to disk
        with open(edited_script_path, "w", encoding="utf-8") as f:
            f.write('\n'.join(data.get("setup_commands", [])))
        generated_files.append(edited_script_path)

    full_json_path = os.path.join(out_dir, "environment_setup.json")
    with open(full_json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    generated_files.append(full_json_path)
    
    print(f"Environment artifacts exported to {out_dir}.")
    return generated_files
