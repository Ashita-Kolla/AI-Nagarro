import os
import json
import re
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

PROMPTS_DIR = "prompts"
OUTPUTS_DIR = "outputs"
LOG_FILE = os.path.join(OUTPUTS_DIR, "run_log.txt")
FINAL_OUTPUT = os.path.join(OUTPUTS_DIR, "full_project_context.json")

MODEL_NAME = "gemini-2.0-flash"

STEPS = [
    "step_01_supervisor",
    "step_02_ba",
    "step_03_architect",
    "step_04_developer",
    "step_05_qa",
    "step_06_devops",
    "step_07_pm",
    "step_08_optimisation"
]

def log_action(action):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {action}\n")

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

def load_prompt_template(step_name):
    prompt_path = os.path.join(PROMPTS_DIR, f"{step_name}.md")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()

def build_prompt(template, user_brief):
    prompt = template.replace("{USER_BRIEF}", user_brief)
    
    placeholders = set(re.findall(r"\{([A-Za-z0-9_ ]+)\}", prompt))
    for p in placeholders:
        if p == "USER_BRIEF":
            continue
        
        # Check if "ALL APPROVED OUTPUTS" is in the placeholder
        if "ALL APPROVED OUTPUTS" in p.upper():
            combined = ""
            for step in STEPS:
                step_file = os.path.join(OUTPUTS_DIR, f"{step}.json")
                if os.path.exists(step_file):
                    with open(step_file, "r", encoding="utf-8") as f:
                        combined += f"\n--- {step} ---\n{f.read()}\n"
            prompt = prompt.replace("{" + p + "}", combined)
            continue
            
        # Try finding a step number in the placeholder like "STEP 2" or "STEP 02"
        match = re.search(r"STEP\s*0?(\d)", p.upper())
        if match:
            step_num = match.group(1)
            target_step = None
            for step in STEPS:
                if f"step_0{step_num}" in step:
                    target_step = step
                    break
            if target_step:
                step_file = os.path.join(OUTPUTS_DIR, f"{target_step}.json")
                if os.path.exists(step_file):
                    with open(step_file, "r", encoding="utf-8") as f:
                        prompt = prompt.replace("{" + p + "}", f.read())
                continue
                
        file_path = os.path.join(OUTPUTS_DIR, f"{p.strip()}.json")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                prompt = prompt.replace("{" + p + "}", f.read())
        else:
            for step in STEPS:
                if step.lower() in p.lower() or p.lower() in step.lower():
                    step_file = os.path.join(OUTPUTS_DIR, f"{step}.json")
                    if os.path.exists(step_file):
                        with open(step_file, "r", encoding="utf-8") as f:
                            prompt = prompt.replace("{" + p + "}", f.read())
    return prompt

def call_llm(client, prompt):
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            max_tokens=1000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"\n[Error calling OpenRouter API]: {e}\n")
        return None

def main():
    if not os.path.exists(OUTPUTS_DIR):
        os.makedirs(OUTPUTS_DIR)

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: OPENROUTER_API_KEY environment variable not found. Please create a .env file.")
        return

    # Using OpenAI SDK with OpenRouter base URL
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    )

    completed_steps = []
    for step in STEPS:
        if os.path.exists(os.path.join(OUTPUTS_DIR, f"{step}.json")):
            completed_steps.append(step)

    start_index = 0
    if completed_steps:
        print(f"Found {len(completed_steps)} completed steps: {', '.join(completed_steps)}")
        ans = input("Do you want to resume from the last approved step? (y/n): ").strip().lower()
        if ans == 'y':
            start_index = len(completed_steps)
            print(f"Resuming from step: {STEPS[start_index] if start_index < len(STEPS) else 'Finished'}")
        else:
            print("Starting fresh. Note: This will overwrite existing output files.")
            log_action("Started fresh run, ignoring previous outputs.")

    if start_index >= len(STEPS):
        print("All steps are already completed. Run finished.")
        return

    user_brief_file = os.path.join(OUTPUTS_DIR, "user_brief.txt")
    if os.path.exists(user_brief_file) and start_index > 0:
        with open(user_brief_file, "r", encoding="utf-8") as f:
            user_brief = f.read()
        print("\nLoaded existing Project Brief.")
    else:
        print("\n--- Project Brief ---")
        user_brief = get_user_brief()
        with open(user_brief_file, "w", encoding="utf-8") as f:
            f.write(user_brief)
        log_action("Received user brief.")

    for i in range(start_index, len(STEPS)):
        step_name = STEPS[i]
        print(f"\n{'='*50}\nExecuting {step_name}...\n{'='*50}")
        
        try:
            template = load_prompt_template(step_name)
        except FileNotFoundError:
            print(f"Error: Prompt file {step_name}.md not found in {PROMPTS_DIR}/ directory.")
            return

        human_note = ""
        while True:
            current_prompt = build_prompt(template, user_brief)
            if human_note:
                current_prompt += f"\n\nHUMAN CORRECTION: {human_note}"

            print(f"Sending prompt for {step_name} to OpenRouter...")
            response_text = call_llm(client, current_prompt)
            
            if response_text is None:
                print("Failed to get response. Quitting.")
                return

            print(f"\n--- Output for {step_name} ---\n")
            print(response_text)
            print("\n-------------------------------\n")

            print("Human Gate Menu:")
            print("[A] Approve and continue")
            print("[E] Edit (provide correction and rerun)")
            print("[R] Regenerate (rerun with no changes)")
            print("[Q] Quit and save progress")
            
            choice = input("\nSelect action [A/E/R/Q]: ").strip().upper()

            if choice == 'A':
                output_path = os.path.join(OUTPUTS_DIR, f"{step_name}.json")
                data = {
                    "step": step_name,
                    "content": response_text
                }
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                log_action(f"Step {step_name} approved.")
                print(f"Saved output to {output_path}")
                break

            elif choice == 'E':
                note = input("Enter your correction: ").strip()
                human_note += f"\n- {note}" if human_note else note
                log_action(f"Step {step_name} edited: {note}")

            elif choice == 'R':
                log_action(f"Step {step_name} regenerated.")
                print("Regenerating...")

            elif choice == 'Q':
                log_action(f"Run paused at {step_name}.")
                print("Quitting. Progress up to the previous step is saved.")
                return

            else:
                print("Invalid choice. Please select A, E, R, or Q.")

    print("\nAll steps completed successfully!")
    log_action("All steps completed successfully.")
    
    full_context = {}
    for step in STEPS:
        path = os.path.join(OUTPUTS_DIR, f"{step}.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                full_context[step] = data.get("content", "")

    with open(FINAL_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(full_context, f, indent=2, ensure_ascii=False)
    
    print(f"Saved combined full project context to {FINAL_OUTPUT}")

if __name__ == "__main__":
    main()
