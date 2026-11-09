from pathlib import Path
import os

from dotenv import load_dotenv

load_dotenv()

DATA_ROOT = Path(os.getenv("DATA_ROOT", r"D:\v-dir-v2"))
CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "chatgpt_conversations")

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2",
)

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1200"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))
BATCH_SIZE = int(os.getenv("INGEST_BATCH_SIZE", "128"))

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "300"))

DEFAULT_TOP_K = int(os.getenv("RAG_TOP_K", "8"))
RETRIEVAL_CANDIDATES = int(os.getenv("RETRIEVAL_CANDIDATES", "40"))
MAX_CONTEXT_CHARS = int(os.getenv("MAX_CONTEXT_CHARS", "14000"))

if CHUNK_SIZE <= 0:
    raise ValueError("CHUNK_SIZE must be greater than zero")
if CHUNK_OVERLAP < 0 or CHUNK_OVERLAP >= CHUNK_SIZE:
    raise ValueError("CHUNK_OVERLAP must be >= 0 and smaller than CHUNK_SIZE")
if BATCH_SIZE <= 0:
    raise ValueError("INGEST_BATCH_SIZE must be greater than zero")
if DEFAULT_TOP_K <= 0 or RETRIEVAL_CANDIDATES <= 0:
    raise ValueError("RAG_TOP_K and RETRIEVAL_CANDIDATES must be greater than zero")
