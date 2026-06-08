"""Milestone 6 - evaluation harness.

Runs each test question through the full pipeline and prints, for every one:
  - the retrieved top-k chunks with their cosine distances (retrieval quality)
  - the grounded answer and the sources it cited (response quality)

Usage:
  .venv/Scripts/python evaluate.py            # the 5 official eval questions
  .venv/Scripts/python evaluate.py --stress   # extra questions to probe failures
"""
import sys

from generator import generate_answer
from vector_store import EVAL_QUESTIONS

# Extra questions used only to hunt for an honest failure case (Milestone 6
# requires at least one). Not part of the official evaluation table.
STRESS_QUESTIONS = [
    "Is David Joyner a good professor for CS 1301?",
    "Is Zhiwu Lin a good CS professor?",
    "Which CS professor gives the most useful feedback?",
]


def run(questions):
    for q in questions:
        print("\n" + "=" * 78)
        print("Q:", q)
        res = generate_answer(q)
        print("\nRETRIEVED CHUNKS (top-5, cosine distance):")
        for i, h in enumerate(res["hits"], 1):
            snippet = h["text"].replace("\n", " ")
            if len(snippet) > 150:
                snippet = snippet[:150] + "..."
            print(f"  [{i}] dist={h['distance']:.3f}  {h['source_file']}")
            print(f"      {snippet}")
        print("\nANSWER:")
        print(" ", res["answer"].replace("\n", "\n  "))
        print("\nSOURCES CITED:", [s["file"] for s in res["sources"]] or "(none)")


if __name__ == "__main__":
    if "--stress" in sys.argv:
        run(STRESS_QUESTIONS)
    else:
        run(EVAL_QUESTIONS)
