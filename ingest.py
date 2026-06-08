"""Milestone 3 - document ingestion.

Loads the plain-text documents in documents/ and pulls the SOURCE url
(line 1 of every file) out into metadata, returning the document body
separately from its source info. No heavy dependencies - standard library only.
"""
from pathlib import Path

DOCS_DIR = Path(__file__).parent / "documents"


def _source_label(body_lines):
    """Build a short, human-readable label describing what a document is about.

    This becomes the per-chunk context prefix in chunker.py, which is what makes
    a chunk self-contained (the professor/thread the opinion is about is carried
    inside the chunk, even when the original sentence never names it).
    """
    for line in body_lines:
        if line.startswith("PROFESSOR:"):
            rest = line[len("PROFESSOR:"):].strip()
            name = rest.split(" - ")[0].split(" — ")[0].strip()
            dept = ""
            for sep in (" — ", " - "):
                if sep in rest:
                    dept = rest.split(sep, 1)[1].split(",")[0].strip()
                    break
            return f"{name}, {dept}".rstrip(", ")
        if line.startswith("TITLE:"):
            return "r/gatech: " + line[len("TITLE:"):].strip()
        if line.startswith("COURSE:"):
            course = line[len("COURSE:"):].replace("—", "-").split("-")[0].strip()
            return f"Course Critique: {course}"
    return "GT CS reviews"


def load_documents(folder=DOCS_DIR):
    """Return a list of dicts: source_file, source_url, source_label, body."""
    docs = []
    for path in sorted(Path(folder).glob("*.txt")):
        raw = path.read_text(encoding="utf-8").splitlines()

        # Line 1 is the "SOURCE: <url>" attribution line - pull it into metadata
        # and strip it from the body so it never ends up inside a chunk.
        source_url = ""
        body_start = 0
        for i, line in enumerate(raw):
            if line.strip().upper().startswith("SOURCE:"):
                source_url = line.split(":", 1)[1].strip()
                body_start = i + 1
                break

        body_lines = raw[body_start:]
        body = "\n".join(body_lines).strip()
        docs.append({
            "source_file": path.name,
            "source_url": source_url,
            "source_label": _source_label(body_lines),
            "body": body,
        })
    return docs


if __name__ == "__main__":
    docs = load_documents()
    print(f"Loaded {len(docs)} documents\n")
    for d in docs:
        print(f"{d['source_file']:34} | {d['source_label']:42} | {d['source_url']}")
