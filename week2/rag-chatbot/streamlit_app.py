import streamlit as st
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


st.set_page_config(
    page_title="RAG Chatbot",
    layout="wide"
)

st.title("RAG Chatbot")
st.write("Ask questions from your PDF")


@st.cache_resource
def load_data():

    loader = PyPDFLoader("data/notes.pdf")
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="chroma_db"
    )

    return db


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


with st.spinner("Loading model and vector database..."):
    db = load_data()
    llm = load_model()

st.success("System Ready!")


query = st.text_input("Ask a question from the PDF")


if st.button("Generate Answer"):

    if query.strip() == "":
        st.warning("Please enter a question")

    else:

        # Retrieval
        results = db.similarity_search(query, k=3)

        context = "\n\n".join(
            [r.page_content for r in results]
        )

        prompt = f"""<|system|>
You are an expert, encouraging, and highly precise AI Study Assistant. Your task is to help the student understand their notes by answering their questions using ONLY the provided context.

Strict Guidelines:
1. Grounding: Answer the question using ONLY the facts explicitly mentioned in the [CONTEXT] block below. Do NOT assume, speculate, or use external knowledge.
2. Missing Information: If the [CONTEXT] does not contain the answer, reply exactly with: "I don't know based on the provided notes."
3. Tone: Maintain a helpful, clear, and encouraging educational tone. Use simple, easily understood language.
4. Style: Keep your answers concise, direct, and well-structured. Use brief bullet points if explaining multiple items.</s>
<|user|>
[CONTEXT]
{context}

[STUDENT_QUESTION]
{query}</s>
<|assistant|>
"""

        # Generate
        with st.spinner("Generating answer..."):

            response = llm(
                prompt,
                max_new_tokens=120,
                temperature=0.3,
                do_sample=True,
                return_full_text=False
            )

            answer = response[0]["generated_text"]

        # Output
        st.subheader("Answer")
        st.write(answer)

        # Show Retrieved Context
        with st.expander("Retrieved Context"):
            for i, r in enumerate(results):
                st.write(f"Chunk {i+1}")
                st.write(r.page_content)
                st.write("------")