# StudyAI — Premium RAG Assistant

StudyAI is an AI-powered Retrieval-Augmented Generation (RAG) assistant that transforms study notes (PDFs) into an interactive learning system. Users can upload documents and then ask questions, generate summaries, or create quizzes based strictly on the uploaded content.

---

## Features

### PDF Upload Support
- Upload study notes in PDF format
- Automatic text extraction and chunking

### RAG-based Question Answering
- Ask questions about uploaded notes
- Answers are grounded only in retrieved document context

### Smart Summarization
- Generate concise summaries of study material

### Quiz Generation
- Automatically generate quizzes from uploaded documents

### Interactive Q&A Interface
- Chat-based system for querying documents

---

## How It Works

### 1. Document Upload
The user uploads a PDF file, which is parsed and split into smaller text chunks.

### 2. Embedding and Storage
Text chunks are converted into embeddings and stored in a vector database.

### 3. Retrieval
When a question is asked, the system retrieves the most relevant chunks from the vector store.

### 4. Response Generation
A language model generates an answer using only the retrieved context, ensuring grounded responses.

---

## Guardrails and Reliability

### Input and Output Guardrails
- Prevents sensitive or unsafe input data
- Ensures outputs remain within document scope
- Reduces irrelevant or harmful responses

### Pydantic Validation
- Enforces structured LLM outputs
- Ensures required fields such as answer and sources
- Helps reduce hallucinations by validating response format

---

## Document Statistics

After uploading a file, the system displays:
- Source file name
- Total number of pages
- Number of text chunks created

---

## Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/your-username/studyai.git
cd studyai
