import os
from typing import List, Dict

import numpy as np
import streamlit as st
from dotenv import load_dotenv
from groq import Groq, APIConnectionError, APIStatusError, RateLimitError
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

load_dotenv()

st.set_page_config(page_title="Chat with PDFs | GenAI V5", page_icon="📚", layout="wide")

DEFAULT_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
TOP_K = 4

SYSTEM_PROMPT = """You are a helpful document question-answering assistant.
Answer using only the supplied document context.
If the answer is not present in the context, clearly say that you could not find it in the uploaded PDFs.
Do not invent facts. Cite supporting sources using the supplied [filename, page N] labels.
You may explain the answer in simple language, and use bullet points when useful."""

@st.cache_resource
def load_embedding_model():
    return SentenceTransformer(EMBEDDING_MODEL)


def split_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Split extracted page text into overlapping character chunks."""
    text = " ".join(text.split())
    if not text:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == len(text):
            break
        start = end - overlap
    return chunks


def extract_pdf_chunks(uploaded_files) -> List[Dict]:
    """Extract text page by page so every chunk keeps its PDF page citation."""
    records = []
    for uploaded_file in uploaded_files:
        reader = PdfReader(uploaded_file)
        for page_number, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text() or ""
            for chunk in split_text(page_text):
                records.append({
                    "text": chunk,
                    "source": uploaded_file.name,
                    "page": page_number,
                })
    return records


def retrieve_relevant_chunks(question: str, records: List[Dict], embeddings: np.ndarray, model):
    query_embedding = model.encode(
        [question],
        convert_to_numpy=True,
        normalize_embeddings=True,
    )[0]
    scores = embeddings @ query_embedding
    best_indices = np.argsort(scores)[::-1][:TOP_K]
    return [
        {**records[int(index)], "score": float(scores[int(index)])}
        for index in best_indices
    ]


def build_context(matches: List[Dict]) -> str:
    sections = []
    for item in matches:
        source_label = f"[{item['source']}, page {item['page']}]"
        sections.append(f"{source_label}\n{item['text']}")
    return "\n\n---\n\n".join(sections)


if "pdf_records" not in st.session_state:
    st.session_state.pdf_records = []
if "pdf_embeddings" not in st.session_state:
    st.session_state.pdf_embeddings = None
if "indexed_signature" not in st.session_state:
    st.session_state.indexed_signature = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "indexed_files" not in st.session_state:
    st.session_state.indexed_files = []

st.title("📚 Chat with Your PDFs")
st.caption("V5 · Retrieval Augmented Generation (RAG) · Local embeddings + Groq")

with st.sidebar:
    st.header("1. Upload documents")
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type=["pdf"],
        accept_multiple_files=True,
        help="Text-based PDFs are supported. Scanned image-only PDFs need OCR, which is not included in V5.",
    )

    model_id = st.text_input("Groq model ID", value=DEFAULT_MODEL)
    top_k = st.slider("Relevant chunks to retrieve", min_value=1, max_value=8, value=TOP_K)

    index_clicked = st.button("Process PDFs", type="primary", use_container_width=True)
    clear_clicked = st.button("Clear chat", use_container_width=True)

    if clear_clicked:
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption("Embedding model")
    st.code(EMBEDDING_MODEL)
    st.caption("Embeddings run locally. Groq is used only to generate answers.")

if index_clicked:
    if not uploaded_files:
        st.sidebar.warning("Upload at least one PDF first.")
    else:
        try:
            with st.spinner("Reading PDFs and creating local embeddings..."):
                records = extract_pdf_chunks(uploaded_files)
                if not records:
                    st.session_state.pdf_records = []
                    st.session_state.pdf_embeddings = None
                    st.session_state.indexed_files = []
                    st.sidebar.error("No extractable text found. This may be a scanned/image-only PDF.")
                else:
                    embedding_model = load_embedding_model()
                    texts = [record["text"] for record in records]
                    vectors = embedding_model.encode(
                        texts,
                        convert_to_numpy=True,
                        normalize_embeddings=True,
                        show_progress_bar=False,
                    )
                    st.session_state.pdf_records = records
                    st.session_state.pdf_embeddings = vectors
                    st.session_state.indexed_files = [file.name for file in uploaded_files]
                    st.session_state.messages = []
                    st.sidebar.success(f"Indexed {len(records)} text chunks.")
        except Exception as exc:
            st.sidebar.error("Could not process the PDFs.")
            st.sidebar.code(str(exc))

if st.session_state.pdf_records:
    st.success(
        f"Ready to chat with {len(st.session_state.indexed_files)} PDF(s) "
        f"({len(st.session_state.pdf_records)} indexed chunks)."
    )
    with st.expander("View indexed documents"):
        for filename in st.session_state.indexed_files:
            st.write(f"📄 {filename}")
else:
    st.info("Upload one or more PDFs in the sidebar, then click **Process PDFs**.")

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.warning("GROQ_API_KEY is missing. Add it to your .env file.")
    st.code("GROQ_API_KEY=your_actual_groq_api_key")
    st.stop()

# Render earlier turns. The chat history is kept in Streamlit session state.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            with st.expander("Sources used"):
                for source in message["sources"]:
                    st.write(f"- {source}")

question = st.chat_input(
    "Ask a question about your uploaded PDFs...",
    disabled=not bool(st.session_state.pdf_records),
)

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Searching your PDFs and generating an answer..."):
                embedding_model = load_embedding_model()
                matches = retrieve_relevant_chunks(
                    question,
                    st.session_state.pdf_records,
                    st.session_state.pdf_embeddings,
                    embedding_model,
                )
                context = build_context(matches)

                # Send the retrieved document context and recent chat turns to Groq.
                conversation = [{"role": "system", "content": SYSTEM_PROMPT}]
                history = st.session_state.messages[:-1][-6:]
                conversation.extend(history)
                conversation.append({
                    "role": "user",
                    "content": (
                        "Use the following retrieved PDF context to answer the question.\n\n"
                        f"DOCUMENT CONTEXT:\n{context}\n\n"
                        f"QUESTION:\n{question}"
                    ),
                })

                client = Groq(api_key=api_key, timeout=60.0, max_retries=2)
                result = client.chat.completions.create(
                    model=model_id.strip(),
                    messages=conversation,
                    temperature=0.2,
                    max_tokens=1200,
                )
                answer = result.choices[0].message.content or "No answer was returned."
                source_labels = list(dict.fromkeys(
                    f"{item['source']} — page {item['page']}" for item in matches
                ))

            st.markdown(answer)
            with st.expander("Retrieved PDF passages"):
                for item in matches:
                    st.markdown(
                        f"**{item['source']} — page {item['page']}** "
                        f"(similarity: {item['score']:.3f})"
                    )
                    st.write(item["text"])

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sources": source_labels,
            })

        except RateLimitError:
            st.error("Groq free-tier rate limit reached. Wait and try again.")
            st.session_state.messages.pop()
        except APIConnectionError:
            st.error("Could not connect to Groq. Check your internet connection.")
            st.session_state.messages.pop()
        except APIStatusError as exc:
            st.error(f"Groq API error ({exc.status_code}). Check your API key and model ID.")
            st.code(str(exc))
            st.session_state.messages.pop()
        except Exception as exc:
            st.error("An error occurred while searching or answering.")
            st.code(str(exc))
            st.session_state.messages.pop()
