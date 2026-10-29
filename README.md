# Mainframe Knowledge Search — retrieval, measured (W5)

Week 5 of the original 12-week plan, picked up after the capstone:
**prove retrieval works before adding a chatbot.** No answer generation
in this project — if the right passage isn't retrieved, no polished
answer layer can rescue it. (Project 3 skipped this step and jumped
straight to answers; this project does it properly.)

## What it does

Indexes a small synthetic mainframe corpus — COBOL copybooks, batch
runbooks, incident notes, all clearly labeled SYNTHETIC — and searches
it three ways (vector, BM25, hybrid RRF) over two chunking strategies
(fixed windows vs structure-aware), scored against 25 golden questions
with known relevant passages.

Every result carries **provenance**: source file, section, score.

## Quickstart

```bash
pip install -r requirements.txt
cp .env.example .env   # OPENAI_API_KEY (embeddings only; pennies)

python scripts/ask.py "What does file status 39 mean?"
python scripts/ask.py "Which job loads transactions?" --method vector --chunking fixed

python scripts/benchmark.py   # the metric table -> results/benchmark.md
```

## The corpus (synthetic, internally consistent)

- `corpus/copybooks/` — CUSTREC, ACCTREC, TXNREC record layouts
- `corpus/runbooks/` — nightly batch, S0C7 abends, VSAM status codes, job restart
- `corpus/incidents/` — two incident notes that reference the copybooks and runbooks

## Metrics

- **Hit rate@k** — fraction of questions with a relevant passage in the top k
- **Recall@k** — fraction of all relevant passages found in the top k
- **MRR** — mean reciprocal rank of the first relevant passage

Relevance is judged by span overlap with the golden section, so
fixed-size chunks straddling section boundaries are scored fairly.

## Design choices

- Embeddings cached on disk by content hash — re-running the benchmark
  never re-buys the same vectors.
- No vector database: numpy cosine over a tiny corpus. A real vector DB
  is a production concern (see the plan's Week 9), not a retrieval-
  quality concern at this scale.
- Structure-aware chunking splits on markdown headings and COBOL
  01-levels — the document's own boundaries.

## What I learned

- Retrieval can be measured before generation exists — and should be; a chatbot would have hidden every failure I found.
- Chunking moved the numbers more than retriever choice. The boring layer is the load-bearing one.
- Fixed windows won on this corpus partly by accident: boundary bleed smuggled neighboring context into every chunk.
- Structure chunks fail by isolation — a section that doesn't repeat its document's key terms is invisible.
- BM25 and vector have opposite blind spots (exact tokens vs. paraphrase), and their scores can't be averaged — rank fusion exists because the scales are incommensurable.
- A reranker fixes ranking, never recall. Whether a failure is one or the other is a measurement (pool membership), not an opinion.
- Contextual prefixes reallocate strength; they don't add it. Every fix I measured created or revealed a cost somewhere else.
- A benchmark that saturates (hit rate 1.0) has stopped measuring — MRR and harder questions are how you keep it honest.
