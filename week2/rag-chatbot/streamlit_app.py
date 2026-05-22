import streamlit as st
import os
import tempfile
import json
import re
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Import simplified schemas and centralized guardrails
from guardrails import (
    AnswerSchema,
    SummarySchema,
    QuizQuestion,
    QuizSchema,
    check_input_guardrail,
    parse_and_validate_answer,
    parse_and_validate_summary,
    parse_and_validate_quiz,
    redact_sensitive_ip
)

# Set page configuration
st.set_page_config(
    page_title="StudyAI - Smart RAG Companion",
    
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Modern Glassmorphic Theme CSS Custom Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
    }

    .stApp {
        background: #0b0f19;
        color: #f1f5f9;
    }

    /* Gradient header text */
    .gradient-text {
        background: linear-gradient(135deg, #818cf8 0%, #c084fc 50%, #f472b6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        margin-bottom: 0.5rem;
    }

    .subtitle-text {
        font-size: 1.1rem;
        color: #94a3b8;
        margin-bottom: 2rem;
    }

    /* Glassmorphic Container Cards */
    .glass-card {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 18px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px 0 rgba(0, 0, 0, 0.25);
    }

    .sidebar-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 16px;
        margin-top: 15px;
    }

    /* Custom styled buttons with smooth hover micro-animations */
    div.stButton > button {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
        color: white !important;
        border: none !important;
        padding: 12px 28px !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.3) !important;
        width: 100% !important;
    }

    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5) !important;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
    }

    div.stButton > button:active {
        transform: translateY(0) !important;
    }

    /* Custom styling for inputs */
    div.stTextInput > div > div > input {
        background-color: rgba(15, 23, 42, 0.4) !important;
        color: #f1f5f9 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 10px !important;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: rgba(30, 41, 59, 0.3) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_model():
    model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)

    llm = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        device=-1
    )
    return llm


def process_pdf(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        temp_pdf_path = tmp_file.name

    try:
        loader = PyPDFLoader(temp_pdf_path)
        docs = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,
            chunk_overlap=50
        )
        chunks = splitter.split_documents(docs)

        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        db = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings
        )
        return db, len(docs), len(chunks)
    finally:
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)


@st.cache_resource
def load_default_db():
    if os.path.exists("data/notes.pdf"):
        loader = PyPDFLoader("data/notes.pdf")
        docs = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)
        chunks = splitter.split_documents(docs)
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        db = Chroma.from_documents(documents=chunks, embedding=embeddings)
        return db, len(docs), len(chunks)
    return None, 0, 0


# Sidebar Design
st.sidebar.markdown("""
<div style='text-align: center; margin-bottom: 20px;'>
    <h2 style='font-size: 2rem; color: #818cf8; margin-bottom: 0px;'>StudyAI</h2>
    <p style='font-size: 0.9rem; color: #94a3b8;'>Your Premium RAG Assistant</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.subheader(" Upload Notes")
uploaded_file = st.sidebar.file_uploader("Upload your study notes PDF", type="pdf")

# Load model (cached)
with st.spinner("Loading AI model (TinyLlama-1.1B)..."):
    llm = load_model()

# Process Vector DB
db = None
num_pages = 0
num_chunks = 0

if uploaded_file is not None:
    if 'current_file' not in st.session_state or st.session_state.current_file != uploaded_file.name:
        with st.spinner("Analyzing and parsing uploaded PDF..."):
            db, num_pages, num_chunks = process_pdf(uploaded_file)
            st.session_state.db = db
            st.session_state.num_pages = num_pages
            st.session_state.num_chunks = num_chunks
            st.session_state.current_file = uploaded_file.name
    else:
        db = st.session_state.db
        num_pages = st.session_state.num_pages
        num_chunks = st.session_state.num_chunks
else:
    if os.path.exists("data/notes.pdf"):
        if 'current_file' not in st.session_state or st.session_state.current_file != "default_notes":
            with st.spinner("Loading default notes (data/notes.pdf)..."):
                db, num_pages, num_chunks = load_default_db()
                st.session_state.db = db
                st.session_state.num_pages = num_pages
                st.session_state.num_chunks = num_chunks
                st.session_state.current_file = "default_notes"
        else:
            db = st.session_state.db
            num_pages = st.session_state.num_pages
            num_chunks = st.session_state.num_chunks

# Sidebar stats card
if db is not None:
    source_name = uploaded_file.name if uploaded_file else 'data/notes.pdf'
    st.sidebar.markdown(f"""
    <div class="sidebar-card">
        <h4 style="color: #c084fc; margin-top: 0px; margin-bottom: 8px;">Document Stats</h4>
        <p style="margin: 0px; font-size: 0.9rem;"><b>Source:</b> {source_name}</p>
        <p style="margin: 4px 0px; font-size: 0.9rem;"><b>Total Pages:</b> {num_pages}</p>
        <p style="margin: 0px; font-size: 0.9rem;"><b>Text Chunks:</b> {num_chunks}</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.sidebar.warning("⚠️ No document loaded. Please upload a PDF to get started.")

# Main screen layout
st.markdown("""
<div>
    <h1 class="gradient-text">StudyAI</h1>
    <p class="subtitle-text">Transform your study notes into an interactive RAG session. Ask questions, generate comprehensive summaries, or test yourself with quizzes.</p>
</div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["Ask Questions", "Summarize Notes", "Generate Quiz"])

# TAB 1: ASK QUESTIONS
with tab1:
    st.markdown("""
    <div class="glass-card">
        <h3 style="color: #818cf8; margin-top: 0px; margin-bottom: 8px;">Interactive Q&A</h3>
        <p style="color: #94a3b8; font-size: 0.95rem; margin-bottom: 0px;">Ask any question about your notes. The AI Study Assistant will search your notes and provide a factual, grounded answer.</p>
    </div>
    """, unsafe_allow_html=True)

    query = st.text_input("Ask a question about the document:", placeholder="e.g., What are the main topics discussed in Chapter 2?", key="qa_query")

    if st.button("Get Answer", key="btn_get_answer"):
        if not query.strip():
            st.warning("Please enter a question to generate an answer.")
        elif db is None:
            st.error("No document database loaded. Please upload a PDF first.")
        else:
            # 1. Input Guardrail
            is_safe, error_msg = check_input_guardrail(query)
            if not is_safe:
                st.warning(error_msg)
            else:
                # Retrieval
                with st.spinner("Searching document database..."):
                    results = db.similarity_search(query, k=3)
                    context = "\n\n".join([r.page_content for r in results])

                # Prompt template (ChatML optimized, forcing structured JSON schema)
                prompt = f"""<|system|>
You are an expert, encouraging, and highly precise AI Study Assistant.
Your task is to help the student understand their notes by answering their questions using ONLY the provided context.

Strict Guidelines:
1. Return your response ONLY as a valid JSON object matching the schema below.
2. Do not include any introductory remarks, conversation, or markdown backticks (like ```json).
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

                # Generation
                with st.spinner("Generating precise structured answer..."):
                    response = llm(
                        prompt,
                        max_new_tokens=150,
                        temperature=0.1,  # Ultra-low temperature for high factuality
                        do_sample=True,
                        return_full_text=False
                    )
                    raw_answer = response[0]["generated_text"]

                # 2. Output Validation and Groundedness check
                parsed_ans = parse_and_validate_answer(raw_answer, context)

                if not parsed_ans.grounded:
                    st.warning("⚠️ Ungrounded Response Rejected: The system detected that the answer cannot be verified using your uploaded notes. Reverting to fallback statement.")
                    st.markdown(f"""
                    <div class="glass-card" style="border-left: 5px solid #f59e0b;">
                        <h4 style="color: #f59e0b; margin-top: 0px;">💡 Notice</h4>
                        <p style="font-size: 1.05rem; line-height: 1.6; margin-bottom: 0px;">I don't know based on the provided notes.</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Display Answer
                    st.markdown(f"""
                    <div class="glass-card" style="border-left: 5px solid #818cf8;">
                        <h4 style="color: #818cf8; margin-top: 0px;">💡 Answer</h4>
                        <p style="font-size: 1.05rem; line-height: 1.6; white-space: pre-wrap; margin-bottom: 0px;">{parsed_ans.answer}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Display Validated Sources
                    if parsed_ans.sources:
                        st.markdown("##### Verified Sources:")
                        for s in parsed_ans.sources:
                            st.info(f"“{s}”")

                # Display retrieved chunks
                with st.expander("Show Retrieved Notes (Context Source)"):
                    for idx, r in enumerate(results):
                        redacted_content = redact_sensitive_ip(r.page_content)
                        st.markdown(f"""
                        <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.05); padding: 12px; border-radius: 8px; margin-bottom: 10px;">
                            <span style="color: #c084fc; font-weight: 600; font-size: 0.95rem;">Chunk {idx+1} (Source Context)</span>
                            <p style="font-size: 0.9rem; color: #cbd5e1; margin-top: 5px; margin-bottom: 0px; white-space: pre-wrap;">{redacted_content}</p>
                        </div>
                        """, unsafe_allow_html=True)

# TAB 2: SUMMARIZE NOTES
with tab2:
    st.markdown("""
    <div class="glass-card">
        <h3 style="color: #c084fc; margin-top: 0px; margin-bottom: 8px;">📝 Academic Note Summarizer</h3>
        <p style="color: #94a3b8; font-size: 0.95rem; margin-bottom: 0px;">Enter a specific topic or keyword to summarize, or leave it empty to synthesize the general highlights of the notes.</p>
    </div>
    """, unsafe_allow_html=True)

    topic = st.text_input("Enter a topic to summarize (optional):", placeholder="e.g., neural networks, photosynthesis, machine learning (leave empty for general)", key="summarize_topic")

    if st.button("Generate Summary", key="btn_summarize"):
        if db is None:
            st.error("No document database loaded. Please upload a PDF first.")
        else:
            # 1. Input Guardrail
            is_safe, error_msg = check_input_guardrail(topic if topic.strip() else "general overview")
            if not is_safe:
                st.warning(error_msg)
            else:
                search_query = topic.strip() if topic.strip() else "general overview study guide keys definitions"
                
                with st.spinner("Synthesizing source context..."):
                    results = db.similarity_search(search_query, k=4)
                    context = "\n\n".join([r.page_content for r in results])

                prompt = f"""<|system|>
You are an expert academic summarizer. Your task is to synthesize the provided notes into a structured JSON summary.

Strict Guidelines:
1. Return your response ONLY as a valid JSON object matching the schema below.
2. Do not include any introductory remarks, conversation, or markdown backticks (like ```json).
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

Please summarize the above notes.</s>
<|assistant|>
"""

                with st.spinner("Synthesizing professional summary..."):
                    response = llm(
                        prompt,
                        max_new_tokens=220,
                        temperature=0.3,
                        do_sample=True,
                        return_full_text=False
                    )
                    raw_summary = response[0]["generated_text"]

                # 2. Output Validation
                parsed_sum = parse_and_validate_summary(raw_summary)

                # Display Summary
                display_topic = topic.strip() if topic.strip() else 'General Notes Summary'
                st.markdown(f"""
                <div class="glass-card" style="border-left: 5px solid #c084fc;">
                    <h4 style="color: #c084fc; margin-top: 0px;">Summary: {display_topic}</h4>
                    <p style="font-size: 1.05rem; line-height: 1.6; white-space: pre-wrap; margin-bottom: 15px;">{parsed_sum.summary}</p>
                </div>
                """, unsafe_allow_html=True)

                # Render Extracted Key Concepts in styled tags
                if parsed_sum.key_concepts:
                    st.markdown("##### Extracted Key Concepts:")
                    concepts_html = "".join([f'<span style="background: rgba(192, 132, 252, 0.15); color: #c084fc; border: 1px solid rgba(192, 132, 252, 0.3); padding: 5px 12px; border-radius: 20px; font-size: 0.9rem; font-weight: 500; margin-right: 8px; display: inline-block; margin-bottom: 8px;">🔑 {concept}</span>' for concept in parsed_sum.key_concepts])
                    st.markdown(concepts_html, unsafe_allow_html=True)

# TAB 3: GENERATE QUIZ
with tab3:
    st.markdown("""
    <div class="glass-card">
        <h3 style="color: #f472b6; margin-top: 0px; margin-bottom: 8px;">Dynamic Quiz Generator</h3>
        <p style="color: #94a3b8; font-size: 0.95rem; margin-bottom: 0px;">Generate three custom quiz questions based on a specific topic in your notes to test your comprehension.</p>
    </div>
    """, unsafe_allow_html=True)

    quiz_topic = st.text_input("Enter a topic for the quiz:", placeholder="e.g., backpropagation, cell division, history concepts", key="quiz_topic")

    if st.button("Generate 3-Question Quiz", key="btn_quiz"):
        if not quiz_topic.strip():
            st.warning("Please enter a topic to focus the quiz.")
        elif db is None:
            st.error("No document database loaded. Please upload a PDF first.")
        else:
            # 1. Input Guardrail
            is_safe, error_msg = check_input_guardrail(quiz_topic)
            if not is_safe:
                st.warning(error_msg)
            else:
                with st.spinner("Extracting content for quiz questions..."):
                    results = db.similarity_search(quiz_topic, k=4)
                    context = "\n\n".join([r.page_content for r in results])

                prompt = f"""<|system|>
You are an academic instructor and quiz designer. Your task is to generate 3 quiz questions based on the context.

Strict Guidelines:
1. Return your response ONLY as a valid JSON object matching the schema below.
2. Do not include introductory text, conversation, or markdown backticks (like ```json).
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

Please generate the quiz based on the notes.</s>
<|assistant|>
"""

                with st.spinner("Designing interactive quiz questions..."):
                    response = llm(
                        prompt,
                        max_new_tokens=250,
                        temperature=0.5,
                        do_sample=True,
                        return_full_text=False
                    )
                    raw_quiz = response[0]["generated_text"]

                # 2. Output Validation
                parsed_quiz = parse_and_validate_quiz(raw_quiz)

                # Display Quiz in a beautiful interactive card layout
                st.markdown(f"""
                <div style="margin-bottom: 15px;">
                    <h4 style="color: #f472b6;">Study Quiz: {quiz_topic}</h4>
                </div>
                """, unsafe_allow_html=True)
                
                for idx, q in enumerate(parsed_quiz.questions):
                    st.markdown(f"""
                    <div class="glass-card" style="border-left: 5px solid #f472b6; padding: 18px; margin-bottom: 12px;">
                        <span style="color: #f472b6; font-weight: 700; font-size: 1rem;">Question {idx+1}</span>
                        <p style="font-size: 1.05rem; font-weight: 500; margin-top: 5px; margin-bottom: 10px;">{q.question}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with st.expander(f"Reveal Hint & Answer for Question {idx+1}"):
                        st.markdown(f"**Hint:** *{q.hint}*")
                        st.success(f"**Answer Key:** {q.answer}")