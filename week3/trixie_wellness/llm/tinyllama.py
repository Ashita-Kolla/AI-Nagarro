import torch
from transformers import pipeline as hf_pipeline

MODEL_ID = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
_pipe = None

def get_pipeline():
    global _pipe
    if _pipe is None:
        device = 0 if torch.cuda.is_available() else -1
        dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        _pipe = hf_pipeline(
            "text-generation",
            model=MODEL_ID,
            torch_dtype=dtype,
            device=device,
        )
    return _pipe

def chat(
    system_prompt: str,
    user_message: str,
    max_new_tokens: int = 200,
    temperature: float = 0.3,
) -> str:
    pipe = get_pipeline()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_message},
    ]
    prompt = pipe.tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )
    output = pipe(
        prompt,
        max_new_tokens=max_new_tokens,
        do_sample=True,
        temperature=temperature,
        top_p=0.9,
        pad_token_id=pipe.tokenizer.eos_token_id,
    )
    generated = output[0]["generated_text"]
    if "<|assistant|>" in generated:
        reply = generated.split("<|assistant|>")[-1].strip()
    else:
        reply = generated[len(prompt):].strip()
    return reply
