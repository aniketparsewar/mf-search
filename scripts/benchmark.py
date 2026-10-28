"""Run the full W5 benchmark: 2 chunking strategies x 3 retrievers x 25
golden questions. Prints the metric table (the milestone) and writes
results/benchmark.md with per-question detail for failure analysis.

Run from the project root:  python scripts/benchmark.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv()

from src.chunking import chunk_corpus  # noqa: E402
from src.corpus import load_corpus  # noqa: E402
from src.index import Index  # noqa: E402
from src.metrics import evaluate  # noqa: E402
from src.search import search  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
QUESTIONS = json.loads((ROOT / "evals" / "questions.json").read_text(encoding="utf-8"))
METHODS = ["vector", "bm25", "hybrid"]
K = 5


def main() -> None:
    docs = load_corpus()
    print(f"corpus: {len(docs)} documents")
    lines = ["# W5 Benchmark — Mainframe Knowledge Search", "",
             f"Questions: {len(QUESTIONS)} · k = {K}", "",
             "| Chunking | Retriever | Hit rate | Recall@k | MRR |",
             "|----------|-----------|----------|----------|-----|"]
    for strategy in ["fixed", "structure"]:
        chunks = chunk_corpus(docs, strategy)
        index = Index(chunks)
        print(f"{strategy}: {len(chunks)} chunks")
        for method in METHODS:
            run = {q["question"]: search(index, q["question"], method, k=K)
                   for q in QUESTIONS}
            m = evaluate(run, QUESTIONS, docs, k=K)
            lines.append(
                f"| {strategy} | {method} | {m['hit_rate']} | {m['recall']} | {m['mrr']} |")
            misses = [p for p in m["per_question"] if p["found"] < p["of"]]
            lines += ["", f"## {strategy} + {method} — misses ({len(misses)})"]
            lines += [f"- {p['question']} (found {p['found']}/{p['of']})"
                      for p in misses] or ["- none"]
    table = "\n".join(lines)
    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    (out / "benchmark.md").write_text(table + "\n", encoding="utf-8")
    print("\n" + table)
    print("\nwrote results/benchmark.md")


if __name__ == "__main__":
    main()
