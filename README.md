# The Unofficial Guide — Project 1

A small RAG system that answers plain-language questions about Georgia Tech
Computer Science courses and professors, grounded only in real student reviews.

**Run it:**
```bash
python -m venv .venv && source .venv/Scripts/activate   # Windows Git Bash
pip install -r requirements.txt
cp .env.example .env        # then paste your free Groq key from console.groq.com
python vector_store.py      # one-time: embed chunks into ChromaDB
python app.py               # open the printed http://127.0.0.1:7860
```

---

## Domain

My system covers Computer Science course and professor reviews at Georgia Tech.

This knowledge is valuable because the official course catalog only lists what
topics a class covers. It says nothing about whether a professor explains things
well, whether the exams are fair, or how heavy the workload is. That information
lives in scattered, unofficial places — Rate My Professors, the r/gatech
subreddit, and Course Critique — where students speak honestly. My system pulls
that material into one place so a student can ask a question in plain English and
get a grounded answer with sources, instead of reading dozens of reviews.

---

## Document Sources

10 documents collected as plain-text files in `documents/` (each file starts with
a `SOURCE:` line holding its URL, which the pipeline turns into citation metadata).

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Rate My Professors | Professor reviews (David Joyner) | https://www.ratemyprofessors.com/professor/2267953 |
| 2 | Rate My Professors | Professor reviews (Ellen Zegura) | https://www.ratemyprofessors.com/professor/2578159 |
| 3 | Rate My Professors | Professor reviews (Mark Riedl) | https://www.ratemyprofessors.com/professor/2199464 |
| 4 | Rate My Professors | Professor reviews (Zhiwu Lin, Math) | https://www.ratemyprofessors.com/professor/1238183 |
| 5 | r/gatech | Thread: lowest RateMyProfessor rating at GT | https://www.reddit.com/r/gatech/comments/134ek02/ |
| 6 | r/gatech | Thread: CS classes ranked hardest to easiest | https://www.reddit.com/r/gatech/comments/v87chm/ |
| 7 | r/gatech | Thread: worst-designed classes (incl. CS 2340) | https://www.reddit.com/r/gatech/comments/z3y54a/ |
| 8 | r/gatech | Thread: coolest profs at Tech | https://www.reddit.com/r/gatech/comments/1k3i97g/ |
| 9 | Course Critique | CS 1331 GPA + grade distribution by instructor | https://critique.gatech.edu |
| 10 | Rate My Professors | Professor reviews (Keith McGreggor) | https://www.ratemyprofessors.com/professor/2512045 |

---

## Chunking Strategy

**Chunk size:** One review or one Reddit comment per chunk (a structure-aware
split, not a fixed character window). In practice chunks run ~87–683 characters.
A hard ceiling of ~800 characters is enforced; any single unit longer than that
is sliding-window split at ~600 chars.

**Overlap:** None between separate units, because each review/comment is already a
complete thought. Overlap (~100 chars) is only applied inside an over-long unit
that has to be split. In this corpus no unit exceeded the 800-char ceiling, so in
practice overlap never fired and every chunk is one whole review/comment.

**Why these choices fit my documents:** My documents are not long guides — they
are stacks of short, independent opinions. The natural unit of meaning is one
review or one comment, so that is what one chunk is. A fixed 500-char window would
cut reviews mid-sentence and merge two unrelated reviews together, which pollutes
retrieval. The harder problem in this data is that *the subject is usually not in
the sentence* — a review says "one of the worst professors I have taken" but the
name "Zegura" only appears in the file header. To fix that, every chunk gets a
context line prepended, e.g. `[Source: Ellen Zegura, Computer Science]` or the
Reddit thread title, so the professor/course the opinion is about is embedded in
the chunk itself and the chunk is retrievable on its own. Preprocessing before
chunking: the `SOURCE:` URL line is stripped into metadata, and section markers
like `--- REVIEWS ---` are dropped.

**Final chunk count:** 55 chunks across 10 documents (avg 342 chars).

---

## Sample Chunks

Five representative chunks, each labeled with its source document. Note the
`[Source: ...]` prefix added to every chunk so it carries its subject and is
retrievable on its own.

**1. `01_rmp_joyner.txt`**
> [Source: David Joyner, Computer Science] [Jun 5, 2026] CS1301 | Grade: B+ | Quality 1.0 | Difficulty 5.0 | Tags: Tough grader, Lots of homework
> In my experience, this professor was rarely available and seemed overwhelmed by the number of courses he was teaching. The exams were extremely difficult, and the TAs handled most of the teaching and student support. I would not recommend taking this class if you have other options. He's barely a professor at that point.

**2. `02_rmp_zegura.txt`**
> [Source: Ellen Zegura, Computer Science] [Aug 16, 2023] CS2050 | Grade: A | Quality 1.0 | Difficulty 2.0
> Kind lady, but not good at teaching.

**3. `03_rmp_riedl.txt`**
> [Source: Mark Riedl, Computer Science] [Dec 26, 2025] CS3600 | Grade: A+ | Quality 4.0 | Difficulty 2.0 | Would take again: Yes
> The exams felt fair and received a generous curve. The professor is smart and kind, though clearly overqualified. Note that homework is long and worth 15% each, so be very careful with hidden test cases. I recommend visiting office hours to have the TAs double-check your submission logic and test cases within gradescope.

**4. `06_reddit_class_difficulty.txt`**
> [Source: r/gatech: CS majors, rank the classes you took from hardest to easiest?] POST: Or just drop which classes you found the absolute hardest/on the easier side besides some of the obvious ones (Lin Alg, Multivariable, CS1301/1331, PHYS). Id appreciate it!

**5. `09_coursecritique.txt`**
> [Source: Course Critique: CS 1331] COURSE: CS 1331 — Introduction to Object Oriented Programming (3 Credit Hours)
> DESCRIPTION: Introduction to techniques and methods of object-oriented programming such as encapsulation, inheritance, and polymorphism. Emphasis on software development and individual programming skills.

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via sentence-transformers (384-dimensional),
stored in a persistent ChromaDB collection using cosine distance. It runs locally
with no API key or rate limits, is fast on CPU, and is strong on the short English
sentences that make up this corpus. Semantic search with it matches "is Zegura a
good teacher" to a review that says "not good at teaching" even though they share
almost no exact words. Retrieval is top-k = 5: each chunk is a single short
opinion, so several are needed to capture consensus without diluting the context.

**Production tradeoff reflection:** If cost weren't a constraint and this served
real students, I'd weigh a larger hosted model such as OpenAI `text-embedding-3-large`
or `voyage-3`. They give higher accuracy on nuanced, opinion-heavy text and longer
context windows (useful if I later ingested long advising guides instead of short
reviews). The tradeoffs are real, though: API embeddings add per-call cost and
network latency, introduce a rate-limit dependency, and send student data to a
third party — a privacy concern for anonymous reviews. Local MiniLM avoids all of
that. For an English-only campus corpus at this scale, local MiniLM is the right
call; I'd only move to a hosted model if evaluation showed retrieval was the
bottleneck (and my failure case below suggests the bottleneck is query *type*, not
the embedder).

---

## Retrieval Test Results

Three queries run through `retrieve()` (cosine distance; lower = more relevant),
showing the top returned chunks. Produced with `python evaluate.py`.

**Query 1: "According to Course Critique, what is the average GPA for CS 1331?"**
| Rank | Distance | Source | Chunk (start) |
|---|---|---|---|
| 1 | 0.244 | `09_coursecritique.txt` | "OVERALL: Average GPA 3.04 / 4.0 across 331 sections..." |
| 2 | 0.362 | `09_coursecritique.txt` | "GPA BY INSTRUCTOR (GPA, then %A / %B...)" |
| 3 | 0.420 | `06_reddit_class_difficulty.txt` | "gtthrowaway24: ...Critique - critique.gatech.edu contains historical GPAs..." |

*Why these are relevant:* The top two hits are the exact Course Critique chunks
for CS 1331, and chunk 1 literally contains "Average GPA 3.04 / 4.0," so the
answer is directly supported. The very low distance (0.244) reflects that the
query and the chunk share both topic (CS 1331 GPA) and vocabulary. Chunk 3 is a
weaker but still on-topic match — it's the Reddit comment that *recommends*
Course Critique for GPA data, which is conceptually related even though it doesn't
contain the number.

**Query 2: "Should I take CS 2050 with Ellen Zegura?"**
| Rank | Distance | Source | Chunk (start) |
|---|---|---|---|
| 1 | 0.510 | `02_rmp_zegura.txt` | "One of the worst professors I have taken at this school..." |
| 2 | 0.527 | `02_rmp_zegura.txt` | "PROFESSOR: Ellen Zegura ... OVERALL QUALITY: 1.9 / 5..." |
| 3 | 0.535 | `02_rmp_zegura.txt` | "Kind lady, but not good at teaching." |

*Why these are relevant:* All three top hits come from Zegura's review file and
all concern CS 2050 specifically — exactly the professor/course in the query. This
is the payoff of the `[Source: Ellen Zegura]` prefix on each chunk: the third
review ("Kind lady, but not good at teaching") never names her in the sentence,
yet it still ranks because her name was embedded into the chunk. The system has
the right evidence to conclude "no."

**Query 3: "Are Mark Riedl's exams curved?"**
| Rank | Distance | Source | Chunk (start) |
|---|---|---|---|
| 1 | 0.508 | `03_rmp_riedl.txt` | "The exams felt fair and received a generous curve..." |
| 2 | 0.537 | `03_rmp_riedl.txt` | "...the midterm and final exam did have generous curves." |
| 3 | 0.615 | `10_rmp_mcgreggor.txt` | "[McGreggor] Probably the most fascinating lectures..." (off-topic) |

*Why these are relevant:* The top two chunks are Riedl reviews that explicitly
mention exams receiving a "generous curve," directly answering the question. Note
the #3 hit jumps to distance 0.615 and is an unrelated McGreggor review — a useful
illustration that only the first two results carry real signal, which is why
top-k = 5 plus the model's grounding instruction matters (it ignores the weak hit).

---

## Grounded Generation

**System prompt grounding instruction:** The generator (`generator.py`) sends the
LLM (Groq `llama-3.3-70b-versatile`, temperature 0.2) a system prompt that
restricts it to the retrieved chunks:

> Use ONLY the information in the CONTEXT. Do not use any outside knowledge. If the
> CONTEXT does not contain the answer, reply exactly: "I don't have information
> about that in the collected reviews." Do not guess or invent details. Students
> often disagree — if the CONTEXT shows conflicting opinions, present both sides
> instead of averaging them. Refer to the sources you used by their bracket number,
> e.g. [1], [3].

Structurally, the retrieved chunks are formatted as a numbered list with each
chunk's source URL, and only the top-5 chunks are ever passed in, so the model
physically cannot see the rest of the corpus. The "say you don't know" instruction
is verified: asking "What is the best dining hall at Georgia Tech?" (out of domain)
returns the refusal sentence rather than a hallucinated answer.

**How source attribution is surfaced in the response:** The model cites chunks by
bracket number. After generation, `generate_answer()` parses the `[n]` citations
out of the answer and maps them back to those chunks' source URLs, so the
"Sources" shown under each answer are exactly the documents the answer actually
drew from. A refusal cites no sources (correct). The Gradio UI also has a
"Show the chunks that were retrieved" panel exposing the raw chunks and distances.

---

## Example Responses

Two grounded responses (source attribution visible in the output text) and one
out-of-scope query showing the refusal. These are verbatim system outputs.

**Example 1 — grounded, with attribution**
> **Q:** According to Course Critique, what is the average GPA for CS 1331?
> **A:** The average GPA for CS 1331 is 3.04 / 4.0, according to the Course Critique [1].
> **Sources:** `09_coursecritique.txt` — https://critique.gatech.edu

**Example 2 — grounded, with attribution**
> **Q:** Do students recommend taking CS 2050 with Ellen Zegura?
> **A:** No, students do not recommend taking CS 2050 with Ellen Zegura. According to the reviews [1] and [3], students have expressed dissatisfaction with her teaching style, with one student stating "just don't take her" [1] and another saying "not good at teaching" [3]. The overall quality rating is also low, with a 1.9/5 rating and only 15% of students saying they would take the class again [2].
> **Sources:** `02_rmp_zegura.txt` — https://www.ratemyprofessors.com/professor/2578159

**Example 3 — out-of-scope query (refusal)**
> **Q:** What is the best dining hall at Georgia Tech?
> **A:** I don't have information about that in the collected reviews.
> **Sources:** (none — the answer was not found in the reviews)

Dining halls are outside this corpus (it only covers CS courses/professors), so
the grounding instruction makes the model decline instead of inventing an answer.

---

## Query Interface

The interface is a local Gradio web app (`python app.py`, served at
`http://127.0.0.1:7860`).

**Input field:**
- *Your question* — a single free-text box where the user types a natural-language
  question about GT CS courses or professors. Five clickable example questions are
  provided below the box. Pressing Enter or clicking **Ask** submits.

**Output fields:**
- *Answer* — the grounded answer, followed by a **Sources** list of clickable links
  to the documents the answer cited (or a note that nothing was cited on a refusal).
- *Show the chunks that were retrieved* — a collapsible panel listing each of the
  top-5 retrieved chunks with its cosine distance and source filename, so a user
  can see exactly what evidence the answer was built from.

**Sample interaction transcript:**
```
[User types in "Your question":]
  Are Mark Riedl's exams in CS 3600 curved?

[Answer panel shows:]
  According to [1] and [2], yes, the exams in CS3600 with Mark Riedl are curved.
  Both reviews mention that the exams had "generous curves".

  ---
  Sources
  - 03_rmp_riedl.txt  (https://www.ratemyprofessors.com/professor/2199464)

[Expanding "Show the chunks that were retrieved":]
  [1] distance 0.508 · 03_rmp_riedl.txt
      > [Source: Mark Riedl, Computer Science] ... The exams felt fair and
        received a generous curve...
  [2] distance 0.537 · 03_rmp_riedl.txt
      > [Source: Mark Riedl, Computer Science] ... both the midterm and final
        exam did have generous curves.
  ... (3 more)
```

---

## Evaluation Report

All five questions were run through the full pipeline (`python evaluate.py`).
Retrieval quality is judged from the top-result cosine distance and whether the
correct source document was the #1 hit.

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Average GPA for CS 1331 (Course Critique)? | 3.04 / 4.0 | "3.04 / 4.0 across 331 sections," cites Course Critique | Relevant (dist 0.244, correct source #1) | Accurate |
| 2 | Do students recommend CS 2050 with Ellen Zegura? | No — called one of the worst, bad lectures, harsh grading | "No," reports dissatisfaction, 1.9/5, only 15% would retake | Relevant (dist 0.510, all top hits from Zegura's file) | Accurate |
| 3 | In CS 3600 with Mark Riedl, are exams curved? | Yes — generous curves, though math/concept heavy | "Yes," both reviews mention generous curves | Relevant (dist 0.508, correct source #1) | Accurate |
| 4 | How does CS 1332 difficulty compare to CS 1331? | 1331 easy, 1332 medium/harder, prof-dependent | "1332 medium, 1331 easy," notes it depends on professor | Relevant (dist 0.330, correct thread) | Accurate |
| 5 | What do students say about the TAs in Joyner's CS 1301? | TAs handle most teaching/support; prof rarely available | TAs handled most teaching/support due to prof unavailability; notes no direct TA-quality evaluation | Relevant (dist 0.462, correct source #1) | Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target
**Response accuracy:** Accurate / Partially accurate / Inaccurate

The five planned questions all passed because each is answerable from a *single*
fact-bearing chunk. Because that risked an unrealistically perfect result, I
additionally stress-tested the system with comparative and off-domain questions
(`python evaluate.py --stress`), which surfaced the genuine failure documented below.

---

## Failure Case Analysis

**Question that failed:** "Which CS professor gives the most useful feedback?"

**What the system returned:** "I don't have information about that in the collected
reviews." — a refusal, even though the corpus *does* contain feedback-related
material (Keith McGreggor was criticized because he "did not give helpful comments
to class presentations," and Mark Riedl's reviews discuss homework feedback and
office-hour help).

**Root cause (tied to the retrieval stage):** This is a *comparative / superlative*
query — answering it requires ranking every professor against each other, but
semantic retrieval only returns chunks individually similar to the query phrase.
No single chunk says "professor X gives the most useful feedback," because that
judgment is distributed across many separate reviews — and my chunking deliberately
keeps each review in its own chunk. The top retrieved hit (distance 0.478) was a
Reddit comment about *where to find* instructor opinion surveys, matched on shallow
keyword overlap ("feedback"/"opinion") rather than actual feedback quality. With
weak, off-target context the model correctly refused instead of inventing a name,
so generation behaved well; the failure is upstream, in the mismatch between
per-chunk similarity search and a question that needs corpus-wide aggregation. A
related symptom appeared in the Joyner stress question, where a Zhiwu Lin
(Mathematics) review — "He is an amazing professor" — leaked into the top-5 at
distance 0.421, showing the embedder can't distinguish praise for a CS professor
from praise for a non-CS one.

**What I would change to fix it:** (1) Add **metadata filtering / per-professor
aggregation** — retrieve per professor, then have the model compare summaries —
rather than a single flat top-5. (2) Add **hybrid keyword (BM25) + semantic search**
so literal mentions of "feedback" (e.g. McGreggor's "did not give helpful comments")
are surfaced even when the embedding match is weak. (3) Store a `department` field
in metadata and filter to CS so non-CS reviews (Zhiwu Lin) can't leak into CS
queries. These are listed as stretch features in `planning.md`.

---

## Spec Reflection

**One way the spec helped me during implementation:** The Chunking Strategy section
of `planning.md` was specific enough to translate almost directly into code. Because
I had already decided "one review/comment per chunk, with a source-context line
prepended," `chunker.py` had a clear target: split on blank-line boundaries, drop
markers, and prefix each chunk. Writing that decision down first meant I never wrote
a generic fixed-size splitter and then had to debug why retrieval was returning
half-sentences — the spec ruled that out before any code existed.

**One way my implementation diverged from the spec, and why:** The spec specified a
~100-character overlap for over-long units, but once I measured the real corpus the
largest chunk was only 683 characters, under the 800-char ceiling, so the
overlap/splitting path never executes — effective overlap is zero. I also added a
step that wasn't in the spec: parsing the `[n]` citations out of the model's answer
so the displayed sources are only the ones actually used, after I noticed the first
version listed all five retrieved sources even for a "don't know" answer. Both
changes came from looking at real output rather than the plan.

---

## AI Usage

**Instance 1 — chunking implementation**

- *What I gave the AI:* My Documents and Chunking Strategy sections from
  `planning.md`, plus the actual file format (each file's `SOURCE:` line and the
  `--- REVIEWS ---` / comment structure), and asked it to implement the loader and
  chunker.
- *What it produced:* `ingest.py` (`load_documents()` pulling the SOURCE URL into
  metadata) and `chunker.py` doing a structure-aware split with the source-context
  prefix and an 800-char ceiling.
- *What I changed or overrode:* I made the core design decisions myself — choosing
  one-review-per-chunk over fixed-size or whole-document chunking, and top-k = 5 —
  and verified the output by inspecting random chunks and the per-document counts
  before trusting it.

**Instance 2 — grounded generation and attribution**

- *What I gave the AI:* The Grounded Response requirement and my Retrieval Approach
  section, asking for a generator that answers only from retrieved chunks and cites
  sources.
- *What it produced:* `generator.py` with the grounding system prompt and a Groq
  call, plus the Gradio interface in `app.py`.
- *What I changed or overrode:* The first version listed every retrieved source
  under the answer, including for refusals. I directed a change so attribution
  parses the `[n]` citations the model actually used, and confirmed the grounding
  by running an out-of-corpus question ("best dining hall") and checking it refused.
