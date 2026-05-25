import re
import json
from pydantic import BaseModel, Field, ValidationError

# PYDANTIC SCHEMAS
class AnswerSchema(BaseModel):
    answer: str = Field(description="The factual, concise answer based only on the context.")
    grounded: bool = Field(description="True if the answer is fully supported by the context, False otherwise.")
    sources: list[str] = Field(default=[], description="Exact sentences or quotes from the context supporting the answer.")

class SummarySchema(BaseModel):
    summary: str = Field(description="Structured academic summary of the notes.")
    key_concepts: list[str] = Field(default=[], description="List of core terms, keywords, or topics extracted.")

class QuizQuestion(BaseModel):
    question: str = Field(description="The quiz question.")
    answer: str = Field(description="Answer key.")
    hint: str = Field(description="Helpful study hint.")

class QuizSchema(BaseModel):
    questions: list[QuizQuestion] = Field(description="List of 3 generated questions.")


# INPUT GUARDRAILS
UNSAFE_KEYWORDS = [
    "hack", "bypass", "illegal", "exploit", "malware", "virus", "bomb", "weapon", "kill", "harm", 
    "suicide", "hate", "racist", "sexist", "violence", "porn", "abuse", "steal", "drugs"
]

def check_input_guardrail(query: str) -> tuple[bool, str]:
    """Validates the input query size and filters potentially unsafe or malicious requests."""
    query_lower = query.lower().strip()
    
    # 1. Length guardrail
    if len(query_lower) < 3:
        return False, "⚠️ Safety Check: Input is too short. Please provide a clear, study-related question or topic."
        
    # 2. Key-phrase blocking
    for word in UNSAFE_KEYWORDS:
        if re.search(r'\b' + re.escape(word) + r'\b', query_lower):
            return False, f"⚠️ Safety Flagged: The query contains a potentially sensitive, unsafe, or restricted term ('{word}'). Please ask only academic or study-related questions."
            
    return True, ""


# IP & SENSITIVE INFORMATION REDACTION
def redact_sensitive_ip(text: str) -> str:
    """Detects and redacts sensitive Intellectual Property (IP), credentials, passwords,

    and PII from text before it is displayed or stored.
    """
    if not text:
        return text
    
    # 1. Redact emails
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    text = re.sub(email_pattern, "[REDACTED EMAIL]", text)
    
    # 2. Redact phone numbers (avoiding common simple integers)
    phone_pattern = r'\b(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
    text = re.sub(phone_pattern, "[REDACTED PHONE]", text)
    
    # 3. Redact API keys, passwords, credentials assignments
    # Matches api_key = "value" or sk_live_...
    cred_pattern = r'(?i)\b(?:api_key|password|passwd|secret_key|secret|token|credentials|private_key)\b\s*[:=]\s*["\']([^"\']+)["\']'
    def cred_replacer(match):
        full_match = match.group(0)
        secret_val = match.group(1)
        return full_match.replace(secret_val, "REDACTED_CONFIDENTIAL_IP")
    text = re.sub(cred_pattern, cred_replacer, text)
    
    # Generic HuggingFace, OpenAI, or stripe-like API key patterns
    sk_pattern = r'\b(?:sk|hf|pk)_(?:live|test|ref)?_[a-zA-Z0-9]{24,48}\b'
    text = re.sub(sk_pattern, "[REDACTED API KEY]", text)

    # 4. Redact custom proprietary/IP markings
    # Matches confidential: value or proprietary: value
    ip_pattern = r'(?i)\b(?:confidential|proprietary|patent_pending|secret|classified)\b\s*[:\-=]\s*["\']?([a-zA-Z0-9_\-\s]{3,30})["\']?'
    def ip_replacer(match):
        full_match = match.group(0)
        ip_val = match.group(1).strip()
        if ip_val.lower() not in ["information", "data", "note", "notes", "file", "document", "true", "false"]:
            return full_match.replace(ip_val, "REDACTED_IP")
        return full_match
    text = re.sub(ip_pattern, ip_replacer, text)

    return text


# STRICT SOURCE GROUNDING CHECK
def check_source_grounding(source: str, context: str) -> bool:
    """Checks if a cited source sentence physically exists in the retrieved context."""
    # Strip punctuation and spaces to perform clean comparison
    clean_source = re.sub(r'[^\w\s]', '', source.lower()).strip()
    clean_context = re.sub(r'[^\w\s]', '', context.lower()).strip()
    if not clean_source:
        return False
    return clean_source in clean_context


# RESILIENT LLM OUTPUT PARSERS
def parse_and_validate_answer(raw_text: str, context: str) -> AnswerSchema:
    """Parses raw text into AnswerSchema and applies IP redaction & source grounding checks."""
    raw_text = redact_sensitive_ip(raw_text)
    json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    
    parsed_ans = None
    if json_match:
        json_str = json_match.group(0)
        try:
            data = json.loads(json_str)
            # Normalize sources
            if "sources" in data and isinstance(data["sources"], str):
                data["sources"] = [data["sources"]]
            parsed_ans = AnswerSchema(**data)
        except (json.JSONDecodeError, ValidationError):
            pass

    # Resilient fallback parser
    if not parsed_ans:
        text = raw_text.strip()
        is_grounded = True
        if any(phrase in text.lower() for phrase in ["don't know", "dont know", "not mention", "i don't", "not in the notes", "cannot answer"]):
            is_grounded = False
            
        parsed_ans = AnswerSchema(
            answer=text,
            grounded=is_grounded,
            sources=[]
        )

    # Output Grounding Validation
    if parsed_ans.grounded:
        valid_sources = []
        for s in parsed_ans.sources:
            if check_source_grounding(s, context):
                valid_sources.append(s)
        parsed_ans.sources = valid_sources
        
        # If the answer claims it is grounded but has no valid sources AND is not in the context, check safety
        if not parsed_ans.sources and parsed_ans.answer:
            # Check if answer contains "I don't know" style phrases
            if any(phrase in parsed_ans.answer.lower() for phrase in ["don't know", "dont know", "not mention", "i don't", "not in the notes"]):
                parsed_ans.grounded = False

    return parsed_ans


def parse_and_validate_summary(raw_text: str) -> SummarySchema:
    """Parses raw text into SummarySchema and applies IP redaction."""
    raw_text = redact_sensitive_ip(raw_text)
    json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    
    if json_match:
        json_str = json_match.group(0)
        try:
            data = json.loads(json_str)
            if "key_concepts" in data and isinstance(data["key_concepts"], str):
                data["key_concepts"] = [data["key_concepts"]]
            return SummarySchema(**data)
        except (json.JSONDecodeError, ValidationError):
            pass

    # Resilient fallback summary text parser
    text = raw_text.strip()
    concepts = []
    lines = text.split("\n")
    for line in lines:
        match = re.findall(r"\*\*(.*?)\*\*", line)
        if match:
            concepts.extend(match)
            
    return SummarySchema(
        summary=text,
        key_concepts=list(set(concepts))[:5]
    )


def parse_and_validate_quiz(raw_text: str) -> QuizSchema:
    """Parses raw text into QuizSchema and applies IP redaction."""
    raw_text = redact_sensitive_ip(raw_text)
    json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    
    if json_match:
        json_str = json_match.group(0)
        try:
            data = json.loads(json_str)
            if isinstance(data, list):
                data = {"questions": data}
            return QuizSchema(**data)
        except (json.JSONDecodeError, ValidationError):
            pass

    # Resilient fallback quiz text parser
    questions = []
    parts = re.split(r"\d+\.\s+", raw_text)
    for part in parts:
        if not part.strip():
            continue
        lines = part.strip().split("\n")
        q_text = lines[0].strip()
        ans = ""
        hint = ""
        for line in lines[1:]:
            if "answer" in line.lower() or "key" in line.lower():
                ans = line.replace("Answer:", "").replace("answer:", "").replace("Answer key:", "").strip()
            elif "hint" in line.lower():
                hint = line.replace("Hint:", "").replace("hint:", "").strip()
        if q_text:
            questions.append(QuizQuestion(
                question=q_text,
                answer=ans if ans else "Refer to study guide notes.",
                hint=hint if hint else "Read the context carefully."
            ))
            
    if not questions:
        questions.append(QuizQuestion(
            question=raw_text,
            answer="Refer to notes.",
            hint="Read context."
        ))
        
    return QuizSchema(questions=questions[:3])
