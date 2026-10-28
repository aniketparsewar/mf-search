# Mainframe Knowledge Search — project brief (W5)

**Source:** Week 5 of `ai-engineer-3-month-plan.pdf`. Aniket audited
the plan against shipped work on 2026-10-26 and picked W5 himself:
the mainframe thread (W5 → W6 → W10) was skipped entirely when the
executed path substituted the bank-statement domain, and retrieval
measurement is the discipline Project 3 skipped.

**Thesis:** retrieval quality is measurable *before* any answer layer
exists, and the measurement — not vibes — decides chunking and
retrieval choices.

## What's in the scaffold

- `corpus/` — 9 synthetic documents (3 copybooks, 4 runbooks,
  2 incidents), internally consistent: incidents reference copybook
  fields and runbook procedures, so questions can cross document types.
- `src/` — corpus loader (provenance + section spans), two chunking
  strategies, vector + BM25 index (embedding cache), hybrid RRF search,
  hit-rate/recall/MRR metrics with span-overlap relevance.
- `evals/questions.json` — 25 golden questions with known relevant
  passages (file + section).
- `scripts/ask.py` — single-query search with provenance output.
- `scripts/benchmark.py` — 2 chunkers × 3 retrievers × 25 questions →
  `results/benchmark.md`.

## Day plan (Aniket controls the pace)

- **Day 1 — corpus + chunking.** Load the corpus; print both strategies'
  chunks for ACCTREC side by side. Predict which wins on copybooks, and
  why, *before* any numbers exist. Quiz.
- **Day 2 — indexing + search by hand.** ask.py across methods; check
  provenance on every result; find a query where vector and BM25
  disagree and explain why. Quiz.
- **Day 3 — the benchmark.** Run all 6 configs; read the metric table;
  stretch (the plan's own): add a reranker and *measure* whether it
  helps instead of assuming. Quiz.
- **Day 4 — failure analysis.** Pick three retrieval failures from the
  benchmark; name the layer (chunking, indexing, query, corpus) and the
  fix for each. Retrieval report finalized, README "What I learned",
  closing quiz.

## Milestone (from the plan)

A baseline metric table exists · every result preserves source metadata ·
three retrieval failures explained with proposed fixes.

## Sets up

W6 (Mainframe Knowledge Copilot): answer generation + abstention over
this measured baseline. W10's corpus starts here too.
