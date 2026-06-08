"""Milestone 3 - chunking.

Implements the chunking strategy from planning.md:
  - structure-aware split: one review / one Reddit comment per chunk
    (blocks separated by blank lines), NOT a fixed character window
  - a source-context line is prepended to every chunk so it is self-contained
  - ~800 char ceiling: any single unit longer than that is sliding-window split
    at ~600 chars with ~100 char overlap (the only place overlap is used)
"""
import re
from collections import Counter

from ingest import load_documents

MAX_CHARS = 800       # ceiling for a single chunk
SPLIT_TARGET = 600    # window size when an over-long unit must be split
OVERLAP = 100         # overlap between windows of a split unit

# A "block" that is only a section marker like "--- REVIEWS ---" carries no
# content and should be dropped rather than embedded.
_MARKER = re.compile(r"^-{2,}.*-{2,}$")


def _is_marker(block):
    lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
    return bool(lines) and all(_MARKER.match(ln) for ln in lines)


def _split_long(text):
    """Sliding window, used ONLY for a single unit longer than MAX_CHARS.

    Backs off to the nearest space so words aren't cut, and overlaps windows
    by OVERLAP chars so a sentence split at a boundary survives in both halves.
    """
    pieces, start = [], 0
    while start < len(text):
        end = min(start + SPLIT_TARGET, len(text))
        if end < len(text):
            space = text.rfind(" ", start, end)
            if space > start:
                end = space
        pieces.append(text[start:end].strip())
        if end >= len(text):
            break
        start = end - OVERLAP
    return [p for p in pieces if p]


def chunk_text(doc):
    """Chunk a single loaded document into self-contained chunks."""
    prefix = f"[Source: {doc['source_label']}] "
    blocks = re.split(r"\n\s*\n", doc["body"])
    chunks, unit_n = [], 0
    for block in blocks:
        block = block.strip()
        if not block or _is_marker(block):
            continue
        units = _split_long(block) if len(block) > MAX_CHARS else [block]
        for u in units:
            chunks.append({
                "id": f"{doc['source_file']}::{unit_n}",
                "text": prefix + u,
                "source_file": doc["source_file"],
                "source_url": doc["source_url"],
                "source_label": doc["source_label"],
            })
            unit_n += 1
    return chunks


def chunk_documents(docs=None):
    """Chunk every document and return one flat list of chunk dicts."""
    if docs is None:
        docs = load_documents()
    chunks = []
    for d in docs:
        chunks.extend(chunk_text(d))
    return chunks


if __name__ == "__main__":
    import random

    chunks = chunk_documents()
    lengths = [len(c["text"]) for c in chunks]

    print(f"TOTAL CHUNKS: {len(chunks)}")
    print(f"char length: min={min(lengths)}  max={max(lengths)}  "
          f"avg={sum(lengths) // len(lengths)}\n")

    print("chunks per document:")
    for f, n in sorted(Counter(c["source_file"] for c in chunks).items()):
        print(f"  {f:34} {n}")

    print("\n=== 5 RANDOM CHUNKS (inspect for: standalone? has its subject? clean?) ===")
    random.seed(1)
    for c in random.sample(chunks, 5):
        print(f"\n--- {c['id']}   src: {c['source_url']} ---")
        print(c["text"])
