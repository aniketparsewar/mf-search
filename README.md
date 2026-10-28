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

- *(fill in after the project closes)*
