import argparse

from .config import DEFAULT_TOP_K
from .rag import retrieve


def search(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    conversation_id: str | None = None,
    message_id: str | None = None,
) -> None:
    results = retrieve(
        query,
        top_k=top_k,
        conversation_id=conversation_id,
        message_id=message_id,
    )

    if not results:
        print("No matching chunks found.")
        return

    print(f"\nQuestion: {query}")
    print("=" * 90)

    for index, item in enumerate(results, start=1):
        meta = item["metadata"]
        print(f"\n[{index}] Hybrid score: {item['score']:.4f}")
        print(f"Semantic distance: {item['distance']:.4f}")
        print(f"Snapshot : {meta.get('slug')}")
        print(f"Title    : {meta.get('conv_title')}")
        print(f"Author   : {meta.get('author')}")
        print(f"Date     : {meta.get('created_on')}")
        print(f"Conv ID  : {meta.get('conv_id')}")
        print(f"Message  : {meta.get('message_id')}")
        print(f"Chunk    : {meta.get('chunk_index')}")
        print(f"Chunk ID : {item['id']}")
        print("-" * 90)
        print(item["document"])


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Search your ChatGPT conversation archive."
    )
    parser.add_argument("--query", required=True)
    parser.add_argument("--top-k", type=int, default=DEFAULT_TOP_K)
    parser.add_argument("--conversation-id")
    parser.add_argument("--message-id")
    args = parser.parse_args()

    if args.top_k < 1:
        parser.error("--top-k must be at least 1")

    search(
        args.query,
        args.top_k,
        conversation_id=args.conversation_id,
        message_id=args.message_id,
    )


if __name__ == "__main__":
    main()
