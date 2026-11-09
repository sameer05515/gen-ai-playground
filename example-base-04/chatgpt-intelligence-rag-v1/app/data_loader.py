import json
from pathlib import Path
from typing import Any, Iterator


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8-sig") as file:
        return json.load(file)


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    text = (text or "").strip()
    if not text:
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("chunk_overlap must be >= 0 and smaller than chunk_size")

    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))

        # Prefer a paragraph/newline/space boundary when it is reasonably close.
        if end < len(text):
            boundary = max(
                text.rfind("\n\n", start, end),
                text.rfind("\n", start, end),
                text.rfind(" ", start, end),
            )
            if boundary > start + chunk_size // 2:
                end = boundary

        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)

        if end >= len(text):
            break
        start = max(end - overlap, start + 1)

    return chunks


def iter_snapshot_documents(
    snapshot_dir: Path,
    slug: str,
    snapshot_id: str,
    chunk_size: int,
    chunk_overlap: int,
) -> Iterator[tuple[str, str, dict]]:
    conversations_path = snapshot_dir / "conversations.json"
    messages_path = snapshot_dir / "message.json"
    contents_path = snapshot_dir / "message.contents.json"

    required = [conversations_path, messages_path, contents_path]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing required snapshot files: " + ", ".join(missing))

    conversations = read_json(conversations_path)
    messages = read_json(messages_path)
    contents = read_json(contents_path)

    conversations_by_id = {
        str(row.get("id")): row
        for row in conversations
        if row.get("id") is not None
    }

    # Composite key is intentional: the archive contains one message ID reused
    # by two different conversations. An ID-only map can return the wrong row.
    messages_by_key = {}
    messages_by_id = {}
    for row in messages:
        message_id = row.get("id")
        conv_id = row.get("convId")
        if message_id is None:
            continue
        messages_by_key[(str(conv_id), str(message_id))] = row
        messages_by_id.setdefault(str(message_id), row)

    for content_row in contents:
        message_id = content_row.get("id")
        conv_id = content_row.get("convId")
        content = content_row.get("content")

        if message_id is None or not isinstance(content, str) or not content.strip():
            continue

        message = messages_by_key.get((str(conv_id), str(message_id)))
        if message is None:
            message = messages_by_id.get(str(message_id), {})

        actual_conv_id = str(conv_id or message.get("convId") or "")
        conversation = conversations_by_id.get(actual_conv_id, {})
        title = str(conversation.get("title") or "Untitled conversation")
        author = str(message.get("author") or "Unknown")
        created_on = str(message.get("createdOn") or "")

        # Include the title and role in the embedded text so semantic retrieval
        # can use conversational context, not just the raw message body.
        chunks = chunk_text(content, chunk_size, chunk_overlap)
        for chunk_index, chunk in enumerate(chunks):
            document = (
                f"Conversation: {title}\n"
                f"Author: {author}\n"
                f"Message: {chunk}"
            )
            document_id = (
                f"{slug}:{actual_conv_id}:{message_id}:{chunk_index}"
            )
            metadata = {
                "slug": str(slug),
                "snapshot_id": str(snapshot_id),
                "conv_id": actual_conv_id,
                "conv_title": title[:500],
                "message_id": str(message_id),
                "author": author,
                "created_on": created_on,
                "chunk_index": int(chunk_index),
            }
            yield document_id, document, metadata
