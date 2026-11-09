# GenAI PDF Chat Assistant — V5 (RAG)

Ask questions about your own PDF documents. This project demonstrates a simple Retrieval Augmented Generation (RAG) pipeline.

## Features

- Upload one or more text-based PDF files
- Extract text page by page with `pypdf`
- Split text into overlapping chunks
- Create embeddings locally with `sentence-transformers/all-MiniLM-L6-v2`
- Retrieve the most relevant chunks using cosine similarity (NumPy)
- Send retrieved context to Groq for answer generation
- Display retrieved passages and PDF page references
- Keep chat history during the current Streamlit session

## Architecture

```text
PDF upload
   |
   v
Extract text (pypdf)
   |
   v
Chunk text (overlap)
   |
   v
Local embeddings (Sentence Transformers)
   |
   v
Similarity search (NumPy)
   |
   v
Relevant chunks + question
   |
   v
Groq chat completion
   |
   v
Answer with source/page references
```

## Requirements

- Python 3.10+
- Internet connection for Groq API and the first-time embedding-model download
- Groq API key: https://console.groq.com/keys

The embedding model runs locally after it has been downloaded. Groq is used for text generation. Free-tier limits and model availability can change.

## Setup on Windows (PowerShell)

Extract the ZIP, open the folder in VS Code, and run:

```powershell
py -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env`:

```env
GROQ_API_KEY=your_actual_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b
```

Run:

```powershell
.venv\Scripts\python.exe -m streamlit run app.py
```

Open the local URL printed by Streamlit, usually http://localhost:8501.

## How to use

1. Upload one or more PDFs in the sidebar.
2. Click **Process PDFs** and wait for extraction and embedding generation.
3. Ask a question in the chat box.
4. Inspect **Retrieved PDF passages** to see which page chunks were supplied to the model.
5. Ask follow-up questions; recent conversation turns are included as context.

## Important limitations in V5

- Scanned/image-only PDFs are not supported; OCR is not included.
- PDF text extraction quality depends on the source PDF.
- The document index and conversation are held in Streamlit session memory; they are not saved to a database and may disappear when the session ends.
- This is a learning-grade RAG implementation using NumPy similarity search, not a production vector database.
- The first run downloads the embedding model (roughly tens of MB) and may take a few minutes.
- Only retrieved text is sent to Groq. Do not upload confidential documents unless you are permitted to share their contents with the API provider.

## Troubleshooting

- **No text extracted:** The PDF may be scanned. Use a text-based PDF or add OCR in a future version.
- **401:** Verify `GROQ_API_KEY`.
- **404 / model error:** Check currently available model IDs in Groq Console and update `.env` or the sidebar.
- **429:** Wait for your Groq free-tier quota to reset.
- **First run is slow:** Sentence Transformers downloads the embedding model once and caches it.
- **Memory error:** Try fewer/smaller PDFs or reduce `CHUNK_SIZE` and `TOP_K` in `app.py`.

Never commit or share your `.env` file.
