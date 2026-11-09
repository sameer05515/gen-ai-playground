import chromadb
from .config import CHROMA_PATH, COLLECTION_NAME


def get_client():
    return chromadb.PersistentClient(path=CHROMA_PATH)


def get_collection(reset: bool = False):
    client = get_client()

    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
            print(f"Deleted existing collection: {COLLECTION_NAME}")
        except Exception:
            pass

    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
