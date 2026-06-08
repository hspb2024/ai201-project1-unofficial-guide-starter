# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

My system covers Computer Science course and professor reviews at Georgia Tech.

This is useful because the official course catalog only tells you what topics a class covers. It does not
tell you if a professor explains things well, if the exams are fair, or how heavy the workload is. That
kind of info lives in places like Rate My Professors and the r/gatech subreddit, where students share
honest opinions. My system pulls all of that into one place so a student can just ask a question and get
a real answer.

---

## Documents

<!-- Fill in the URL column as you collect each one. See documents/COLLECTION_GUIDE.md for how. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Rate My Professors | David Joyner reviews (intro CS, 4.2/5, polarized) | https://www.ratemyprofessors.com/professor/2267953 |
| 2 | Rate My Professors | Ellen Zegura reviews (CS2050, low rated 1.9/5) | https://www.ratemyprofessors.com/professor/2578159 |
| 3 | Rate My Professors | Mark Riedl reviews (CS3600, fair exams + curve) | https://www.ratemyprofessors.com/professor/2199464 |
| 4 | Rate My Professors | Zhiwu Lin reviews (Math prof, polarized/spam case) | https://www.ratemyprofessors.com/professor/1238183 |
| 5 | r/gatech | Thread: lowest RateMyProfessor rating at GT | https://www.reddit.com/r/gatech/comments/134ek02/ |
| 6 | r/gatech | Thread: CS classes ranked hardest to easiest | https://www.reddit.com/r/gatech/comments/v87chm/ |
| 7 | r/gatech | Thread: worst-designed classes (incl. CS 2340) | https://www.reddit.com/r/gatech/comments/z3y54a/ |
| 8 | r/gatech | Thread: coolest profs at Tech | https://www.reddit.com/r/gatech/comments/1k3i97g/ |
| 9 | Course Critique | CS 1331 GPA + grade distribution by instructor | https://critique.gatech.edu |
| 10 | Rate My Professors | Keith McGreggor reviews (CS3790, mixed) | https://www.ratemyprofessors.com/professor/2512045 |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** One review or one Reddit comment per chunk (a structure-aware split, not a fixed
character count). In practice each chunk lands around 100 to 600 characters. I set a hard ceiling of
~800 characters: if a single review or comment is longer than that (for example the long ECE 3741 post
in doc 07), it gets split at ~600 characters.

**Overlap:** None between separate units, because each review/comment is already a complete, independent
thought. The only place I use overlap is the ~100-character overlap inside an over-long single unit that
had to be split, so a sentence cut at the boundary still appears in both halves.

**Reasoning:** My documents are not long guides, they are stacks of short opinions. The natural unit of
meaning is one review or one comment, so that is what one chunk should be. A fixed 500-character window
would do two bad things here: cut a review off mid-sentence, and glue the end of one review onto the
start of an unrelated one, which pollutes retrieval. The bigger problem with this data is that the
*subject is usually not in the sentence* — a review says "one of the worst professors I have taken" but
the name "Zegura" only appears in the file header. To fix that, every chunk gets a context line
prepended (e.g. `[Source: Ellen Zegura, CS, 1.9/5]` or the Reddit thread title), so the professor/course
the opinion is about is embedded in the chunk itself and the chunk is retrievable on its own.

How I'd know it's wrong: if chunks were too large (whole-document), a query for one professor's exams
would match the whole blob and the LLM couldn't isolate the relevant line. If they were too small
(half a sentence), retrieval would return fragments with no subject and the answer would be ungrounded.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** `all-MiniLM-L6-v2` via sentence-transformers (384-dimensional). It runs locally with
no API key and no rate limits, it's fast on CPU, and it's strong on short English sentences, which is
exactly what my corpus is. Semantic search with it will match "is Zegura a good teacher" to a review
that says "not good at teaching" even though they share almost no exact words, because the embeddings
capture meaning rather than keywords.

**Top-k:** 5. Each chunk is a single short opinion, so one or two chunks isn't enough to answer
"what do students say about X" — I need several voices to capture the consensus (and the disagreement).
Too few (k=1–2) risks reporting one outlier as if it were the whole story; too many (k=10+) on a small
corpus starts pulling in loosely related chunks that dilute the answer and can push the LLM off-topic.

**Production tradeoff reflection:** If cost weren't a constraint and this served real students, I'd
weigh a larger hosted model such as OpenAI `text-embedding-3-large` or Voyage's `voyage-3`. They give
higher retrieval accuracy on nuanced, opinion-heavy text and longer context windows (useful if I later
chunk long guides instead of short reviews). The tradeoffs: API embeddings add per-call cost and network
latency, create a rate-limit dependency, and send student data to a third party (a privacy concern for
anonymous reviews). MiniLM running locally avoids all of that, so the real decision is accuracy and
multilingual coverage versus cost, latency, and data privacy. For an English-only campus corpus at this
scale, local MiniLM is the right call; I'd only move to a hosted model if evaluation showed retrieval
was the bottleneck.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | According to Course Critique, what is the average GPA for CS 1331? | 3.04 / 4.0 (across 331 sections). Source: doc 09. |
| 2 | Do students recommend taking CS 2050 with Ellen Zegura? | No. Reviews call her one of the worst professors they've had, say her lectures are bad enough that students attend other sections or learn from other profs' slides and YouTube, and that she grades harshly. Source: doc 02. |
| 3 | In CS 3600 with Mark Riedl, are the exams curved? | Yes. Multiple reviews say the exams felt fair and that both the midterm and final received a generous curve, though the exams are math/concept heavy. Source: doc 03. |
| 4 | How do students rank CS 1332's difficulty compared to CS 1331? | CS 1331 is rated "easy" and CS 1332 is rated "medium" (harder than 1331), though difficulty depends on the professor. Source: doc 06. |
| 5 | What do students say about the TAs in David Joyner's CS 1301? | The TAs handle most of the teaching and student support while the professor is rarely available and seems overwhelmed by the number of courses he teaches. Source: doc 01. |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. **Contradictory and polarized reviews.** Some professors get wildly mixed ratings (Zegura is 1.9/5;
   Zhiwu Lin has 54 one-star reviews but also reviews insisting most of those are a spam joke and he's
   actually easy). If retrieval happens to pull mostly one side, the system could confidently report a
   one-sided answer and hide the disagreement. I'll watch for this and want the system to surface both
   views when they exist rather than averaging them away.

2. **The subject lives in the header, not the sentence.** Short reviews/comments rarely repeat the
   professor or course name ("worst class I've taken"), so a chunk on its own may be unattributable and
   un-retrievable for a name-based query. My chunking mitigation (prepending a source/context line to
   every chunk) is aimed squarely at this; if I got that wrong, retrieval accuracy would collapse.

3. **Off-domain noise.** Zhiwu Lin is actually a Mathematics professor who got pulled into a CS thread,
   and some docs discuss ECE classes. A CS-only query could retrieve and cite non-CS content. This is a
   likely source of a documented failure case for Milestone 6.

4. **Sparse data per professor.** A few profs only have 2 reviews collected, so the system may
   overgeneralize from a tiny, possibly skewed sample (e.g. Joyner's file has only negative reviews
   despite his 4.2 overall average).

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

```
  documents/*.txt              ingest.py                 chunker.py
 (10 .txt files,        ┌────────────────────┐    ┌─────────────────────────┐
  SOURCE url on    ───▶ │ 1. INGESTION       │──▶ │ 2. CHUNKING             │
  line 1)              │ read .txt, parse    │    │ one review/comment per  │
                       │ SOURCE url as       │    │ chunk + prepend source  │
                       │ metadata, strip it  │    │ context line            │
                       │ from the body       │    │ (~100-600 chars, no     │
                       └────────────────────┘    │ overlap between units)  │
                                                  └───────────┬─────────────┘
                                                              │
          ┌───────────────────────────────────────────────────┘
          ▼
 ┌──────────────────────────┐        ┌──────────────────────────┐
 │ 3. EMBED + VECTOR STORE   │        │ 4. RETRIEVAL             │
 │ all-MiniLM-L6-v2          │ ─────▶ │ embed query, similarity  │
 │ (sentence-transformers)   │        │ search, return top-k = 5 │
 │ stored in ChromaDB        │        │ chunks + their metadata  │
 │ (local, persistent)       │        └────────────┬─────────────┘
 └──────────────────────────┘                      │
                                                    ▼
                                   ┌──────────────────────────────────┐
        user query ───────────────▶│ 5. GENERATION                    │
        (CLI or Gradio UI)         │ Groq llama-3.3-70b-versatile     │
                                   │ answer grounded ONLY in retrieved │
                                   │ chunks + cite source URLs         │
                                   └──────────────────────────────────┘
```

**Stage → tool:** Ingestion = Python file I/O · Chunking = custom `chunk_text()` · Embedding =
`all-MiniLM-L6-v2` (sentence-transformers) · Vector store = ChromaDB · Generation = Groq
`llama-3.3-70b-versatile`. Interface = CLI or Gradio.

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:** I'll give Claude my Documents section (so it knows the
`SOURCE: <url>` line is on line 1 of every file) and my Chunking Strategy section, and ask it to write
two functions: `load_documents(folder)` that reads each `.txt`, pulls the SOURCE url into a metadata
dict, and returns the body separately; and `chunk_text(doc)` that splits on review/comment boundaries,
enforces the ~800-char ceiling with ~100-char overlap only on over-long units, and prepends the source
context line to each chunk. I'll verify by printing the chunk count and eyeballing 5 chunks to confirm
none cut mid-review and every chunk carries its professor/source.

**Milestone 4 — Embedding and retrieval:** I'll give Claude my Retrieval Approach section and ask it to
embed all chunks with `all-MiniLM-L6-v2`, store them in a persistent ChromaDB collection with their
metadata, and write `retrieve(query, k=5)` that returns the top-5 chunks plus their source URLs. I'll
verify by running my 5 eval questions through retrieval *before* adding generation, checking that the
expected source document appears in the top-5 (testing retrieval in isolation, per the project hint).

**Milestone 5 — Generation and interface:** I'll give Claude the Grounded Response requirement and ask
it to write `generate_answer(query, chunks)` that calls Groq `llama-3.3-70b-versatile` with a system
prompt restricting the model to the retrieved chunks only ("answer only from the context; if it's not
there, say you don't know") and that appends the source URLs it used. Then a small Gradio (or CLI)
front end that takes a question and shows the answer + citations. I'll verify by asking a question whose
answer is NOT in the corpus and confirming it declines instead of hallucinating.
