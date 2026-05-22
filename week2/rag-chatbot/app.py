from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    pipeline
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

        # Retrieve context
        results = db.similarity_search(query, k=3)

        context = "\n\n".join(
            [r.page_content for r in results]
        )

        print("\n--- Retrieved Context ---\n")

        for r in results:
            print(r.page_content[:300])
            print("------")

        # Prompt Engineering
        prompt = f"""<|system|>
You are an expert, encouraging, and highly precise AI Study Assistant. 
Your task is to help the student understand their notes by answering their
 questions using ONLY the provided context.

Strict Guidelines:
1. Grounding: Answer the question using ONLY the facts explicitly mentioned in the 
[CONTEXT] block below. Do NOT assume, speculate, or use external knowledge.
2. Missing Information: If the [CONTEXT] does not contain the answer, reply 
exactly with: "I don't know based on the provided notes."
3. Tone: Maintain a helpful, clear, and encouraging educational tone. Use simple,
 easily understood language.
4. Style: Keep your answers concise, direct, and well-structured.
Use brief bullet points if explaining multiple items.</s>

<|user|>
[CONTEXT]
{context}

[STUDENT_QUESTION]
{query}</s>
<|assistant|>
"""

        response = llm(
            prompt,
            max_new_tokens=120,
            temperature=0.3,
            do_sample=True,
            return_full_text=False
        )

        answer = response[0]["generated_text"]

        print("\n--- FINAL ANSWER ---\n")
        print(answer)

    
    elif choice == "2":

        topic = input("\nEnter topic to summarize: ")

        results = db.similarity_search(topic, k=4)

        context = "\n\n".join(
            [r.page_content for r in results]
        )

        prompt = f"""<|system|>
You are an expert academic summarizer. Your task is to synthesize the provided
 notes into a clear, structured, and student-friendly summary.

Strict Guidelines:
1. Key Concepts: Extract the core themes, terms, and definitions.
2. Formatting: Use bold text for key terms and clean bullet points for readability.
3. Clarity & Tone: Write in a simple, supportive, and engaging educational tone. 
Keep it highly digestible.
4. Grounding: Rely ONLY on the information provided in the [CONTEXT] block below. 
Do not add outside facts.</s>
<|user|>
[CONTEXT]
{context}

Please provide a structured summary of the above notes.</s>
<|assistant|>
"""

        response = llm(
            prompt,
            max_new_tokens=150,
            temperature=0.4,
            do_sample=True,
            return_full_text=False
        )

        summary = response[0]["generated_text"]

        print("\n--- SUMMARY ---\n")
        print(summary)

    
    elif choice == "3":

        topic = input("\nEnter topic: ")

        results = db.similarity_search(topic, k=4)

        context = "\n\n".join(
            [r.page_content for r in results]
        )

        prompt = f"""<|system|>
You are an academic instructor and quiz designer. Your task is to generate 3 short,
 high-quality quiz questions to test a student's understanding of the provided notes.

Strict Guidelines:
1. Source Material: Base the questions ONLY on the provided [CONTEXT] block.
 Do not ask about outside topics.
2. Format: Provide 3 clear questions. For each question, provide a brief hint or answer key.
3. Design: Make the questions direct, clear, and focused on core concepts.
4. Tone: Keep the tone encouraging and academic.</s>
<|user|>
[CONTEXT]
{context}

Please generate the 3 quiz questions based on the above notes.</s>
<|assistant|>
"""

        response = llm(
            prompt,
            max_new_tokens=120,
            temperature=0.7,
            do_sample=True,
            return_full_text=False
        )

        quiz = response[0]["generated_text"]

        print("\n--- QUIZ ---\n")
        print(quiz)

    
    elif choice == "4":

        print("\nGoodbye!")
        break

    else:
        print("\nInvalid option.")