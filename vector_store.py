"""Milestone 4 - embedding, vector store, and retrieval.

Embeds every chunk from chunker.py with all-MiniLM-L6-v2, stores them in a
persistent ChromaDB collection (with source metadata for later attribution),
and exposes retrieve(query, k=5) for semantic search.

Distances are cosine distance (0 = identical meaning, higher = less related),
because the collection is created with hnsw:space="cosine".
"""
import chromadb
from sentence_transformers import SentenceTransformer

from chunker import chunk_documents

MODEL_NAME = "all-MiniLM-L6-v2"
DB_DIR = "chroma_db"
COLLECTION = "gt_cs_reviews"

_model = None


def get_model():
    """Load the embedding model once and reuse it."""
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def build_store(reset=True):
    """Chunk the docs, embed them, and (re)build the ChromaDB collection."""
    chunks = chunk_documents()
    client = chromadb.PersistentClient(path=DB_DIR)

    if reset:
        try:
            client.delete_collection(COLLECTION)
        except Exception:
            pass  # collection didn't exist yet

    coll = client.get_or_create_collection(
        COLLECTION, metadata={"hnsw:space": "cosine"}
    )

    model = get_model()
    embeddings = model.encode(
        [c["text"] for c in chunks], show_progress_bar=True
    ).tolist()

    coll.add(
        ids=[c["id"] for c in chunks],
        documents=[c["text"] for c in chunks],
        embeddings=embeddings,
        metadatas=[
            {
                "source_file": c["source_file"],
                "source_url": c["source_url"],
                "source_label": c["source_label"],
            }
            for c in chunks
        ],
    )
    print(f"Embedded and stored {coll.count()} chunks in '{COLLECTION}'.")
    return coll


def get_collection():
    """Open the existing persistent collection."""
    client = chromadb.PersistentClient(path=DB_DIR)
    return client.get_collection(COLLECTION)


def retrieve(query, k=5, coll=None):
    """Return the top-k chunks for a query, each with source info + distance."""
    if coll is None:
        coll = get_collection()
    q_emb = get_model().encode([query]).tolist()
    res = coll.query(query_embeddings=q_emb, n_results=k)

    hits = []
    for doc, meta, dist in zip(
        res["documents"][0], res["metadatas"][0], res["distances"][0]
    ):
        hits.append({
            "text": doc,
            "source_file": meta["source_file"],
            "source_url": meta["source_url"],
            "distance": dist,
        })
    return hits


# The 5 evaluation questions from planning.md, used to test retrieval in
# isolation (before any LLM is wired in).
EVAL_QUESTIONS = [
    "According to Course Critique, what is the average GPA for CS 1331?",
    "Do students recommend taking CS 2050 with Ellen Zegura?",
    "In CS 3600 with Mark Riedl, are the exams curved?",
    "How do students rank CS 1332's difficulty compared to CS 1331?",
    "What do students say about the TAs in David Joyner's CS 1301?",
]


if __name__ == "__main__":
    build_store(reset=True)
    print("\n" + "=" * 70)
    print("RETRIEVAL TEST - top 3 chunks per evaluation question")
    print("=" * 70)
    for q in EVAL_QUESTIONS:
        print(f"\nQ: {q}")
        for i, h in enumerate(retrieve(q, k=3), 1):
            preview = h["text"].replace("\n", " ")
            if len(preview) > 180:
                preview = preview[:180] + "..."
            print(f"  {i}. dist={h['distance']:.3f}  [{h['source_file']}]")
            print(f"     {preview}")
