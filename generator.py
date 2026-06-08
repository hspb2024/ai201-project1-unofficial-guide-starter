"""Milestone 5 - grounded answer generation.

Retrieves the top-k chunks for a query, then asks Groq's llama-3.3-70b to answer
using ONLY those chunks. Grounding is enforced two ways:
  1. the system prompt forbids outside knowledge and tells it to say it doesn't
     know when the context lacks the answer, and to show disagreement rather
     than average it (our corpus is full of contradictory reviews);
  2. low temperature, and every source URL used is returned for attribution.
"""
import os
import re

from dotenv import load_dotenv
from groq import Groq

from vector_store import retrieve

load_dotenv()
MODEL = "llama-3.3-70b-versatile"

_client = None


def get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=os.environ["GROQ_API_KEY"])
    return _client


SYSTEM_PROMPT = """You are The Unofficial Guide, which answers questions about \
Georgia Tech Computer Science courses and professors using ONLY the student \
reviews provided to you as CONTEXT.

Rules:
- Use ONLY the information in the CONTEXT. Do not use any outside knowledge.
- If the CONTEXT does not contain the answer, reply exactly: "I don't have \
information about that in the collected reviews." Do not guess or invent details.
- Students often disagree. If the CONTEXT shows conflicting opinions, present \
both sides instead of averaging them into one verdict.
- Keep the answer concise and grounded. Refer to the sources you used by their \
bracket number, e.g. [1], [3]."""


def format_context(hits):
    """Number each retrieved chunk so the model can cite it."""
    blocks = []
    for i, h in enumerate(hits, 1):
        blocks.append(f"[{i}] (source: {h['source_url']})\n{h['text']}")
    return "\n\n".join(blocks)


def generate_answer(query, k=5):
    """Return a grounded answer plus the chunks and unique sources behind it."""
    hits = retrieve(query, k=k)
    user_msg = f"CONTEXT:\n{format_context(hits)}\n\nQUESTION: {query}"

    resp = get_client().chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.2,
    )
    answer = resp.choices[0].message.content

    # Attribution should reflect what the answer actually used. Pull the [n]
    # citations out of the answer and map them back to those chunks' sources.
    cited = sorted({int(n) for n in re.findall(r"\[(\d+)\]", answer)})
    sources, seen = [], set()
    if cited:
        for n in cited:
            if 1 <= n <= len(hits):
                h = hits[n - 1]
                if h["source_url"] not in seen:
                    seen.add(h["source_url"])
                    sources.append({"url": h["source_url"], "file": h["source_file"]})
    elif "don't have information" not in answer:
        # Grounded answer that forgot to cite - fall back to all retrieved sources.
        for h in hits:
            if h["source_url"] not in seen:
                seen.add(h["source_url"])
                sources.append({"url": h["source_url"], "file": h["source_file"]})
    # else: a refusal - no sources, which is correct.

    return {"answer": answer, "hits": hits, "sources": sources}


if __name__ == "__main__":
    from vector_store import EVAL_QUESTIONS

    # Two real questions plus one deliberately out-of-corpus question to prove
    # the system declines instead of hallucinating.
    tests = EVAL_QUESTIONS[:2] + [
        "What is the best dining hall at Georgia Tech?"
    ]
    for q in tests:
        r = generate_answer(q)
        print(f"\nQ: {q}")
        print(f"A: {r['answer']}")
        print("Sources used:")
        for s in r["sources"]:
            print(f"   - {s['file']}  {s['url']}")
        print("-" * 70)
