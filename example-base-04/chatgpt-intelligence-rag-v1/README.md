# ChatGPT Intelligence RAG - V2

A local RAG application for searching and asking questions about a ChatGPT JSON archive.

## V2 improvements

- Removed the hardcoded V4 conversation ID from RAG.
- Added optional conversation/message metadata filters from the CLI.
- Retrieves a wider semantic candidate pool and reranks it with lexical term overlap.
- Deduplicates the same message chunk across snapshots while preserving different chunks from the same message.
- Prefers the newest snapshot when duplicate chunks exist.
- Adds source markers (`[S1]`, `[S2]`) to the generation context and asks the LLM not to invent implementation details.
- Makes Ollama model, URL, timeout, retrieval size and context size configurable.
- Adds `requests` to the requirements.
- Keeps ChromaDB local and persistent.

## Requirements

- Python 3.12 recommended
- Ollama installed and running
- `qwen2.5:3b` installed, or another compatible chat model
- ChatGPT archive containing `base.json` and `itr2/`

## Setup (Windows PowerShell)

Activate your existing environment or create one:

```powershell
conda activate chatgpt-rag
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Create `.env` if it does not exist:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and set your archive path:

```env
DATA_ROOT=D:/v-dir-v2
```

Do not commit `.env` or `chroma_db/`. Both may contain private data.

## Build or update the index

First-time indexing:

```powershell
python -m app.ingest
```

Rebuild the entire collection (destructive):

```powershell
python -m app.ingest --reset
```

Use `--reset` only when you intentionally want to delete and rebuild the collection. Normal ingestion uses stable IDs and `upsert`, so rerunning it updates existing chunks.

## Search

General semantic + lexical hybrid search:

```powershell
python -m app.search --query "How did I implement JWT refresh token in Spring Boot?" --top-k 8
```

Filter to one conversation:

```powershell
python -m app.search --query "JWT refresh token rotation" --conversation-id "YOUR_CONVERSATION_ID"
```

Inspect one exact message (all chunks belonging to that message):

```powershell
python -m app.search --query "JWT refresh token" --message-id "YOUR_MESSAGE_ID"
```

## Ask the RAG assistant

Interactive mode:

```powershell
python -m app.rag
```

One-shot mode:

```powershell
python -m app.rag --query "How did I implement JWT refresh token in my React and Spring Boot project?"
```

Print retrieved context before generation:

```powershell
python -m app.rag --show-context
```

Filter to a conversation or exact message when debugging:

```powershell
python -m app.rag --query "Summarize this implementation" --conversation-id "YOUR_CONVERSATION_ID" --show-context
python -m app.rag --query "Summarize this implementation" --message-id "YOUR_MESSAGE_ID" --show-context
```

## Configuration

See `.env.example` for all supported settings.

| Setting | Default | Purpose |
|---|---|---|
| `DATA_ROOT` | `D:\\v-dir-v2` | ChatGPT archive root |
| `CHROMA_PATH` | `./chroma_db` | Persistent ChromaDB directory |
| `COLLECTION_NAME` | `chatgpt_conversations` | Chroma collection |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Local embedding model |
| `CHUNK_SIZE` | `1200` | Characters per chunk |
| `CHUNK_OVERLAP` | `150` | Overlap between chunks |
| `INGEST_BATCH_SIZE` | `128` | Embedding/upsert batch size |
| `RAG_TOP_K` | `8` | Final chunks passed to the LLM |
| `RETRIEVAL_CANDIDATES` | `40` | Semantic candidates before reranking |
| `MAX_CONTEXT_CHARS` | `14000` | Maximum context characters |
| `OLLAMA_URL` | local Ollama API | Chat endpoint |
| `OLLAMA_MODEL` | `qwen2.5:3b` | Local generation model |
| `OLLAMA_TIMEOUT` | `300` | Request timeout in seconds |

## Retrieval design

1. Embed the question locally.
2. Retrieve up to `RETRIEVAL_CANDIDATES` semantic matches from ChromaDB.
3. Deduplicate identical logical chunks across snapshots using `(conv_id, message_id, chunk_index)`.
4. Prefer the highest-numbered snapshot for duplicate chunks.
5. Rerank candidates using semantic similarity plus lexical token overlap.
6. Pass the best `RAG_TOP_K` chunks to Ollama.

The lexical reranker is intentionally lightweight; it is not a full BM25 implementation. It improves exact technical-term matching without adding another dependency.

## Important notes

- A retrieval result is evidence, not proof that every detail in it was implemented. The prompt asks the model to distinguish recorded facts from recommendations and to say when a detail cannot be verified.
- The LLM may still make mistakes. Check the printed source IDs and retrieved context for important answers.
- The application does not upload archive content to an external model API. Embeddings run locally and generation uses your local Ollama server.
- The embedding model may contact Hugging Face during initialization if it is not cached. After it is downloaded, it is reused from the local cache.
