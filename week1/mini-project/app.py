import streamlit as st

from study_assistant import generate_text, init_model



# Read File

def read_uploaded_file(uploaded_file):
    return uploaded_file.read().decode("utf-8")


# Streamlit UI

def load_model():
    return init_model()

st.set_page_config(
    page_title="AI Study Assistant",
    layout="wide",
)

st.title("AI Study Assistant")
st.write("Powered by FLAN-T5 Small")

# Load model
with st.spinner("Loading AI model..."):
    model, tokenizer, device = load_model()

st.success(f"Model loaded on: {device}")

mode = st.sidebar.selectbox(
    "Choose Feature",
    [
        "Summarize Text",
        "Ask Questions",
    ],
)


# SUMMARIZATION

if mode == "Summarize Text":

    st.header(" Text Summarization")

    input_method = st.radio(
        "Choose Input Method",
        [
            "Paste Text",
            "Upload Text File",
        ],
    )

    text = ""

    if input_method == "Paste Text":
        text = st.text_area(
            "Enter text to summarize",
            height=300,
        )

    elif input_method == "Upload Text File":
        uploaded_file = st.file_uploader(
            "Upload .txt file",
            type=["txt"],
        )

        if uploaded_file:
            text = read_uploaded_file(uploaded_file)

            st.subheader("Preview")
            st.text_area(
                "",
                text,
                height=250,
            )

    max_tokens = st.slider(
        "Maximum Summary Length",
        min_value=32,
        max_value=512,
        value=128,
    )

    if st.button("Generate Summary"):

        if not text.strip():
            st.warning("Please enter some text.")
        else:
            with st.spinner("Generating summary..."):
                summary = generate_text(
                    model,
                    tokenizer,
                    device,
                    f"summarize: {text}",
                    max_new_tokens=max_tokens,
                )

            st.subheader("Summary")
            st.success(summary)

# QUESTION ANSWERING

elif mode == "Ask Questions":

    st.header("❓ Ask Questions About Your Notes")

    context = st.text_area(
        "Enter study material / context",
        height=300,
    )

    question = st.text_input(
        "Enter your question",
    )

    max_tokens = st.slider(
        "Maximum Answer Length",
        min_value=16,
        max_value=256,
        value=64,
    )

    if st.button("Get Answer"):

        if not context.strip():
            st.warning("Please enter context.")
        elif not question.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Generating answer..."):

                answer = generate_text(
                    model,
                    tokenizer,
                    device,
                    f"question: {question} context: {context}",
                    max_new_tokens=max_tokens,
                )

            st.subheader("Answer")
            st.success(answer)

# Footer

st.markdown("---")
st.caption("Built with Streamlit + Hugging Face Transformers")