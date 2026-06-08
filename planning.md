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

**Chunk size:**

**Overlap:**

**Reasoning:**

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**

**Top-k:**

**Production tradeoff reflection:**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.

2.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

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

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
