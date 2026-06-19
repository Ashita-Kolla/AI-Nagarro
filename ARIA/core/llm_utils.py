import os
import json
import re
from groq import Groq

MODEL_MAP = {
    "BA": "mixtral-8x7b-32768",
    "Architect": "mixtral-8x7b-32768",
    "Developer": "mixtral-8x7b-32768",
    "QA": "llama3-8b-8192",
    "DevOps": "llama3-8b-8192",
    "PM": "llama3-8b-8192",
    "Supervisor": "llama-3.3-70b-versatile"
}

def call_llm(prompt, agent_name=None, model="llama-3.3-70b-versatile", max_tokens=2000, temperature=0.3):
    """
    Unified LLM caller using Groq API.
    Wraps the call in a try/except block.
    Dynamically switches models based on agent_name if provided.
    """
    if agent_name and agent_name in MODEL_MAP:
        model = MODEL_MAP[agent_name]

    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    try:
        print(f"[LLM] Calling model '{model}' for agent '{agent_name or 'Unknown'}'")
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"\n[Error calling Groq API]: {e}\n")
        return None

def parse_json_from_llm(text):
    """
    Safely extract JSON from the LLM output. 
    Handles conversational text before/after JSON and markdown code blocks.
    """
    if not text:
        return None
    
    text = text.strip()
    
    # 1. Try direct parsing
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
        
    # 2. Try extracting from markdown code block: ```json ... ``` or ``` ... ```
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        candidate = match.group(1).strip()
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    # 3. Try finding the first '{' and last '}'
    start_brace = text.find('{')
    end_brace = text.rfind('}')
    if start_brace != -1 and end_brace != -1 and end_brace > start_brace:
        candidate = text[start_brace:end_brace + 1].strip()
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    # 4. Try finding the first '[' and last ']' (in case of array)
    start_bracket = text.find('[')
    end_bracket = text.rfind(']')
    if start_bracket != -1 and end_bracket != -1 and end_bracket > start_bracket:
        candidate = text[start_bracket:end_bracket + 1].strip()
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    # 5. Failed all extraction
    print("[Error] Failed to parse JSON from LLM output. Raw output was:")
    print(text)
    return None

