from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    pipeline
)

from guardrails import (
    check_input_guardrail,
    parse_and_validate_answer,
    parse_and_validate_summary,
    parse_and_validate_quiz,
    redact_sensitive_ip
)

# 1. LOAD PDF
loader = PyPDFLoader("data/notes.pdf")
docs = loader.load()

print(f"\nPages loaded: {len(docs)}")

# 2. CHUNKING

splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=50
)

chunks = splitter.split_documents(docs)

print(f"Chunks created: {len(chunks)}")


# 3. EMBEDDINGS

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# 4. VECTOR DATABASE

db = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="chroma_db"
)

print("Vector DB ready!")


model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

print("\nLoading model...")

tokenizer = AutoTokenizer.from_pretrained(model_name)

model = AutoModelForCausalLM.from_pretrained(
    model_name
)

llm = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    device=-1
)

print("Model loaded!")


while True:

    print("\n==============================")
    print(" AI STUDY ASSISTANT WITH RAG ")
    print("==============================")
    print("1. Ask Question")
    print("2. Summarize Notes")
    print("3. Generate Quiz")
    print("4. Exit")

    choice = input("\nChoose option: ")

   
    if choice == "1":

        query = input("\nAsk your question: ")

        # 1. Input Guardrail
        is_safe, error_msg = check_input_guardrail(query)
        if not is_safe:
            print(f"\n{error_msg}")
            continue

        # Retrieve context
        results = db.similarity_search(query, k=3)

        context = "\n\n".join(
            [r.page_content for r in results]
        )

        print("\n--- Retrieved Context ---\n")

        for r in results:
            print(redact_sensitive_ip(r.page_content[:300]))
            print("------")

        # Prompt Engineering (forcing JSON schema formatting)
        prompt = f"""<|system|>
You are an expert, encouraging, and highly precise AI Study Assistant. 
Your task is to help the student understand their notes by answering their
 questions using ONLY the provided context.

Strict Guidelines:
1. Return your response ONLY as a valid JSON object matching the schema below.
2. Do not include any introductory remarks, conversation, or markdown backticks.
3. Grounding: Answer the question using ONLY the facts explicitly mentioned in the [CONTEXT]. Do NOT assume or speculate.
4. Missing Information: If the [CONTEXT] does not contain the answer, set grounded to false and write "I don't know based on the provided notes."
5. Format:
{{
  "answer": "Your factual, concise answer here.",
  "grounded": true or false,
  "sources": ["exact sentence 1 from context supporting the answer", "exact sentence 2"]
}}
</s>

<|user|>
[CONTEXT]
{context}

[STUDENT_QUESTION]
{query}</s>
<|assistant|>
"""

        response = llm(
            prompt,
            max_new_tokens=150,
            temperature=0.1,  # Lower temperature for highest factuality
            do_sample=True,
            return_full_text=False
        )

        raw_answer = response[0]["generated_text"]

        # 2. Output Validation and Grounding Verification
        parsed_ans = parse_and_validate_answer(raw_answer, context)

        print("\n--- FINAL ANSWER ---\n")
        if not parsed_ans.grounded:
            print("⚠️ Ungrounded Response Rejected: The system detected that the answer cannot be verified using your uploaded notes. Reverting to fallback statement.")
            print("\nI don't know based on the provided notes.")
        else:
            print(parsed_ans.answer)
            if parsed_ans.sources:
                print("\n📍 Verified Sources:")
                for s in parsed_ans.sources:
                    print(f"“{s}”")

    
    elif choice == "2":

        topic = input("\nEnter topic to summarize: ")

        # 1. Input Guardrail
        is_safe, error_msg = check_input_guardrail(topic if topic.strip() else "general overview")
        if not is_safe:
            print(f"\n{error_msg}")
            continue

        search_query = topic.strip() if topic.strip() else "general overview study guide keys definitions"
        results = db.similarity_search(search_query, k=4)

        context = "\n\n".join(
            [r.page_content for r in results]
        )

        prompt = f"""<|system|>
You are an expert academic summarizer. Your task is to synthesize the provided
 notes into a structured JSON summary.

Strict Guidelines:
1. Return your response ONLY as a valid JSON object matching the schema below.
2. Do not include any introductory remarks, conversation, or markdown backticks.
3. Key Concepts: Extract the core themes, terms, and definitions.
4. Grounding: Rely ONLY on the information provided in the [CONTEXT] block below. Do not add outside facts.
5. Format:
{{
  "summary": "Your structured, student-friendly bullet-point summary text.",
  "key_concepts": ["term 1", "term 2", "term 3"]
}}
</s>
<|user|>
[CONTEXT]
{context}

Please provide a structured summary of the above notes.</s>
<|assistant|>
"""

        response = llm(
            prompt,
            max_new_tokens=220,
            temperature=0.3,
            do_sample=True,
            return_full_text=False
        )

        raw_summary = response[0]["generated_text"]
        parsed_sum = parse_and_validate_summary(raw_summary)

        print("\n--- SUMMARY ---\n")
        print(parsed_sum.summary)
        
        if parsed_sum.key_concepts:
            print("\n🏷️ Extracted Key Concepts:")
            for concept in parsed_sum.key_concepts:
                print(f"🔑 {concept}")

    
    elif choice == "3":

        topic = input("\nEnter topic: ")

        if not topic.strip():
            print("\nPlease enter a topic to focus the quiz.")
            continue

        # 1. Input Guardrail
        is_safe, error_msg = check_input_guardrail(topic)
        if not is_safe:
            print(f"\n{error_msg}")
            continue

        results = db.similarity_search(topic, k=4)

        context = "\n\n".join(
            [r.page_content for r in results]
        )

        prompt = f"""<|system|>
You are an academic instructor and quiz designer. Your task is to generate 3 quiz questions based on the context.

Strict Guidelines:
1. Return your response ONLY as a valid JSON object matching the schema below.
2. Do not include introductory text, conversation, or markdown backticks.
3. Grounding: Base the questions ONLY on the provided [CONTEXT] block.
4. Format:
{{
  "questions": [
    {{
      "question": "Question 1 text?",
      "answer": "Short answer to question 1",
      "hint": "Brief study hint"
    }},
    {{
      "question": "Question 2 text?",
      "answer": "Short answer to question 2",
      "hint": "Brief study hint"
    }},
    {{
      "question": "Question 3 text?",
      "answer": "Short answer to question 3",
      "hint": "Brief study hint"
    }}
  ]
}}
</s>
<|user|>
[CONTEXT]
{context}

Please generate the 3 quiz questions based on the above notes.</s>
<|assistant|>
"""

        response = llm(
            prompt,
            max_new_tokens=250,
            temperature=0.5,
            do_sample=True,
            return_full_text=False
        )

        raw_quiz = response[0]["generated_text"]
        parsed_quiz = parse_and_validate_quiz(raw_quiz)

        print("\n--- QUIZ ---\n")
        for idx, q in enumerate(parsed_quiz.questions):
            print(f"\nQuestion {idx+1}: {q.question}")
            print(f"💡 Hint: {q.hint}")
            print(f"✅ Answer Key: {q.answer}")

    
    elif choice == "4":

        print("\nGoodbye!")
        break

    else:
        print("\nInvalid option.")