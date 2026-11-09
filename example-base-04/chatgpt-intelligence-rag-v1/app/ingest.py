import argparse
from pathlib import Path

from .config import DATA_ROOT, CHUNK_SIZE, CHUNK_OVERLAP, BATCH_SIZE
from .data_loader import read_json, iter_snapshot_documents
from .embeddings import embed_texts
from .vector_store import get_collection


def ingest(data_root: Path, reset: bool = False) -> None:
    base_file = data_root / "base.json"
    if not base_file.exists():
        raise FileNotFoundError(
            f"Could not find {base_file}. DATA_ROOT must contain base.json and itr2/."
        )

    base_rows = read_json(base_file)
    collection = get_collection(reset=reset)

    total_indexed = 0
    processed_snapshots = 0
    skipped_snapshots = 0

    for row in base_rows:
        slug = str(row.get("slug") or "").strip()
        if not slug:
            continue

        snapshot_dir = data_root / "itr2" / slug
        if not snapshot_dir.is_dir():
            skipped_snapshots += 1
            print(f"[SKIP] {slug}: output directory not found")
            continue

        print(f"\n[SNAPSHOT] {slug} - {row.get('id', '')}")
        batch_ids, batch_docs, batch_meta = [], [], []
        snapshot_count = 0

        for doc_id, document, metadata in iter_snapshot_documents(
            snapshot_dir=snapshot_dir,
            slug=slug,
            snapshot_id=str(row.get("id") or ""),
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        ):
            batch_ids.append(doc_id)
            batch_docs.append(document)
            batch_meta.append(metadata)

            if len(batch_ids) >= BATCH_SIZE:
                vectors = embed_texts(batch_docs)
                collection.upsert(
                    ids=batch_ids,
                    documents=batch_docs,
                    metadatas=batch_meta,
                    embeddings=vectors,
                )
                snapshot_count += len(batch_ids)
                total_indexed += len(batch_ids)
                print(f"  Indexed {snapshot_count} chunks...")
                batch_ids, batch_docs, batch_meta = [], [], []

        if batch_ids:
            vectors = embed_texts(batch_docs)
            collection.upsert(
                ids=batch_ids,
                documents=batch_docs,
                metadatas=batch_meta,
                embeddings=vectors,
            )
            snapshot_count += len(batch_ids)
            total_indexed += len(batch_ids)

        processed_snapshots += 1
        print(f"[DONE] {slug}: {snapshot_count} chunks indexed")

    print("\n========== INGESTION SUMMARY ==========")
    print(f"Data root          : {data_root}")
    print(f"Processed snapshots: {processed_snapshots}")
    print(f"Skipped snapshots  : {skipped_snapshots}")
    print(f"Chunks indexed     : {total_indexed}")
    print(f"Collection count   : {collection.count()}")
    print("=======================================")


def main():
    parser = argparse.ArgumentParser(description="Index ChatGPT JSON snapshots into ChromaDB")
    parser.add_argument("--data-root", type=Path, default=DATA_ROOT)
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete and recreate the vector collection before indexing",
    )
    args = parser.parse_args()
    ingest(args.data_root, reset=args.reset)


if __name__ == "__main__":
    main()
