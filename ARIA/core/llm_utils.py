import os
import json
from groq import Groq

def call_llm(prompt, model="llama-3.3-70b-versatile", max_tokens=2000, temperature=0.3):
    """
    Unified LLM caller using Groq API.
    Wraps the call in a try/except block.
    """
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    try:
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
    Sometimes LLMs add markdown code blocks around the JSON.
    """
    if not text:
        return None
    
    try:
        # First, try to parse it directly
        return json.loads(text)
    except json.JSONDecodeError:
        # If it fails, try to strip markdown fences
        text_stripped = text.strip()
        if text_stripped.startswith("```json"):
            text_stripped = text_stripped[7:]
        elif text_stripped.startswith("```"):
            text_stripped = text_stripped[3:]
        
        if text_stripped.endswith("```"):
            text_stripped = text_stripped[:-3]
            
        try:
            return json.loads(text_stripped.strip())
        except json.JSONDecodeError:
            print("[Error] Failed to parse JSON from LLM output. Raw output was:")
            print(text)
            return None
