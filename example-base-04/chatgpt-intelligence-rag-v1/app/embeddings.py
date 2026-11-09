
import torch
from sentence_transformers import SentenceTransformer
from .config import EMBEDDING_MODEL

_model = None

CPU_THREADS = 10
EMBEDDING_BATCH_SIZE = 64


def get_model():
    global _model

    if _model is None:
        torch.set_num_threads(CPU_THREADS)

        _model = SentenceTransformer(
            EMBEDDING_MODEL,
            device="cpu"
        )

        print("Embedding model loaded")
        print(f"CPU threads: {torch.get_num_threads()}")

    return _model


def embed_texts(texts: list[str]):
    model = get_model()

    vectors = model.encode(
        texts,
        batch_size=EMBEDDING_BATCH_SIZE,
        normalize_embeddings=True,
        show_progress_bar=False
    )

    return vectors.tolist()
