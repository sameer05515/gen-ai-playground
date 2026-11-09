import argparse
import re
import sys
from collections import Counter
from typing import Any

import requests

from .config import (
    OLLAMA_URL,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT,
    RETRIEVAL_CANDIDATES,
    DEFAULT_TOP_K,
    MAX_CONTEXT_CHARS,
)


TOKEN_RE = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9_+#.-]*")
STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "did", "do",
    "for", "from", "how", "i", "in", "into", "is", "it", "me", "my",
    "of", "on", "or", "the", "to", "was", "were", "what", "when",
    "where", "which", "who", "why", "with", "would", "you", "your",
}


def tokenize(text: str) -> list[str]:
    return [
        token.lower()
        for token in TOKEN_RE.findall(text or "")
        if token.lower() not in STOP_WORDS and len(token) > 1
    ]


def snapshot_number(slug: str) -> int:
    match = re.search(r"(\d+)$", slug or "")
    return int(match.group(1)) if match else -1


def build_where(conversation_id: str | None, message_id: str | None) -> dict | None:
    clauses = []
    if conversation_id:
        clauses.append({"conv_id": conversation_id})
    if message_id:
        clauses.append({"message_id": message_id})
    if not clauses:
        return None
    return clauses[0] if len(clauses) == 1 else {"$and": clauses}


def retrieve(
    question: str,
    top_k: int = DEFAULT_TOP_K,
    conversation_id: str | None = None,
    message_id: str | None = None,
) -> list[dict[str, Any]]:
    from .vector_store import get_collection

    collection = get_collection()
    count = collection.count()
    if count == 0:
        return []

    from .embeddings import embed_texts

    query_vector = embed_texts([question])[0]
    where = build_where(conversation_id, message_id)

    # Fetch a wider semantic candidate pool, then rerank with lexical relevance.
    candidate_count = min(max(top_k, RETRIEVAL_CANDIDATES), count)
    query_args = {
        "query_embeddings": [query_vector],
        "n_results": candidate_count,
        "include": ["documents", "metadatas", "distances"],
    }
    if where:
        query_args["where"] = where

    result = collection.query(**query_args)
    ids = result.get("ids", [[]])[0]
    docs = result.get("documents", [[]])[0]
    metas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]

    # Deduplicate the same logical chunk across archive snapshots.
    # Preserve different chunks belonging to the same message.
    deduped: dict[tuple, dict[str, Any]] = {}
    for doc_id, doc, meta, distance in zip(ids, docs, metas, distances):
        key = (
            meta.get("conv_id"),
            meta.get("message_id"),
            meta.get("chunk_index"),
        )
        candidate = {
            "id": doc_id,
            "document": doc or "",
            "metadata": meta or {},
            "distance": float(distance),
        }
        current = deduped.get(key)
        if current is None:
            deduped[key] = candidate
        else:
            old_slug = current["metadata"].get("slug", "")
            new_slug = candidate["metadata"].get("slug", "")
            # Prefer the newest snapshot; use lower distance as a tie-breaker.
            if (
                snapshot_number(new_slug) > snapshot_number(old_slug)
                or (
                    snapshot_number(new_slug) == snapshot_number(old_slug)
                    and candidate["distance"] < current["distance"]
                )
            ):
                deduped[key] = candidate

    query_terms = set(tokenize(question))
    ranked = []
    for item in deduped.values():
        distance = item["distance"]
        semantic_score = max(0.0, 1.0 - (distance / 2.0))
        doc_terms = set(tokenize(item["document"]))
        lexical_score = (
            len(query_terms & doc_terms) / len(query_terms)
            if query_terms else 0.0
        )
        # Semantic search remains primary; lexical overlap helps exact technical terms.
        item["score"] = (0.72 * semantic_score) + (0.28 * lexical_score)
        ranked.append(item)

    ranked.sort(key=lambda item: item["score"], reverse=True)
    return ranked[:top_k]


def build_context(results: list[dict[str, Any]]) -> str:
    parts = []
    used_chars = 0

    for index, item in enumerate(results, start=1):
        meta = item["metadata"]
        block = (
            f"[S{index}]\n"
            f"Conversation: {meta.get('conv_title', 'Unknown')}\n"
            f"Author: {meta.get('author', 'Unknown')}\n"
            f"Snapshot: {meta.get('slug', 'Unknown')}\n"
            f"Message ID: {meta.get('message_id', 'Unknown')}\n"
            f"Chunk: {meta.get('chunk_index', 'Unknown')}\n"
            f"Content:\n{item['document']}\n"
        )
        if used_chars + len(block) > MAX_CONTEXT_CHARS:
            remaining = MAX_CONTEXT_CHARS - used_chars
            if remaining > 300:
                parts.append(block[:remaining])
            break
        parts.append(block)
        used_chars += len(block)

    return "\n---\n".join(parts)


def build_prompt(question: str, context: str) -> str:
    return f"""You answer questions about the user's own ChatGPT conversation archive.

Rules:
- Use only facts explicitly supported by the supplied sources.
- The sources may contain different projects or older discussions. Do not merge them.
- Prefer specific project summaries and first-person historical details over generic tutorials.
- Do not invent source code, class names, endpoints, database fields, or implementation steps.
- If a detail is absent, say "I couldn't verify that detail from the retrieved conversations."
- Do not turn a design recommendation into a claim that the user implemented it.
- Answer the question directly and concisely.
- Add source markers such as [S1] after factual claims.
- Do not generate code unless the source contains the relevant code.

Retrieved conversation excerpts:
{context}

Question:
{question}

Answer:"""


def generate_answer(question: str, context: str) -> str:
    prompt = build_prompt(question, context)
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_ctx": 8192,
                "num_predict": 900,
            },
        },
        timeout=OLLAMA_TIMEOUT,
    )
    response.raise_for_status()
    payload = response.json()
    message = payload.get("message", {})
    answer = message.get("content")
    if not answer:
        raise RuntimeError(f"Ollama returned no answer: {payload}")
    return answer.strip()


def ask_question(
    question: str,
    top_k: int = DEFAULT_TOP_K,
    conversation_id: str | None = None,
    message_id: str | None = None,
    show_context: bool = False,
) -> None:
    results = retrieve(
        question,
        top_k=top_k,
        conversation_id=conversation_id,
        message_id=message_id,
    )
    if not results:
        print("No matching chunks found. Check the index or your metadata filters.")
        return

    context = build_context(results)
    if show_context:
        print("\n========== RETRIEVED CONTEXT ==========\n")
        print(context)
        print("\n=======================================\n")

    try:
        answer = generate_answer(question, context)
    except requests.RequestException as exc:
        print(f"Ollama request failed: {exc}")
        print("Check that Ollama is running and the configured model is installed.")
        return

    print("\n========== RAG ANSWER ==========\n")
    print(answer)

    print("\n========== SOURCES ==========\n")
    for index, item in enumerate(results, start=1):
        meta = item["metadata"]
        print(
            f"[S{index}] {meta.get('conv_title')} | "
            f"snapshot={meta.get('slug')} | "
            f"message={meta.get('message_id')} | "
            f"chunk={meta.get('chunk_index')} | "
            f"distance={item['distance']:.4f} | "
            f"score={item['score']:.4f}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ask questions about your indexed ChatGPT conversation archive."
    )
    parser.add_argument("--query", help="Question; omit to enter interactive mode.")
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K)
    parser.add_argument("--conversation-id", help="Optional conversation metadata filter.")
    parser.add_argument("--message-id", help="Optional exact message metadata filter.")
    parser.add_argument(
        "--show-context",
        action="store_true",
        help="Print retrieved excerpts before generating the answer.",
    )
    args = parser.parse_args()

    if args.top_k < 1:
        parser.error("--top-k must be at least 1")

    question = args.query or input("Ask a question about your ChatGPT history: ").strip()
    if not question:
        parser.error("Question cannot be empty.")

    ask_question(
        question,
        top_k=args.top_k,
        conversation_id=args.conversation_id,
        message_id=args.message_id,
        show_context=args.show_context,
    )


if __name__ == "__main__":
    main()
