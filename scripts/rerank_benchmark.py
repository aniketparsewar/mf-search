"""LLM reranker on top of hybrid retrieval; measure vs the unre-ranked
baseline. Stretch for W5 Day 3: do not assume the reranker helps.

Run from the project root:  python scripts/rerank_benchmark.py
"""
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

from src.chunking import chunk_corpus  # noqa: E402
from src.corpus import load_corpus  # noqa: E402
from src.index import Index  # noqa: E402
from src.metrics import evaluate  # noqa: E402
from src.search import search  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
QUESTIONS = json.loads((ROOT / "evals" / "questions.json").read_text(encoding="utf-8"))
MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
K = 5
CANDIDATES = 10

_client_instance = None


def get_client() -> OpenAI:
    """Shared OpenAI client (reads OPENAI_API_KEY from the environment)."""
    global _client_instance
    if _client_instance is None:
        _client_instance = OpenAI()
    return _client_instance


def rerank(question: str, candidates: list[dict], k: int = K) -> list[dict]:
    """Ask the model to order retrieved passages; fall back to original order."""
    if not candidates:
        return []
    numbered = "\n\n".join(
        f"[{i}] {c['file']} :: {c['section']}\n{c['text'][:800]}"
        for i, c in enumerate(candidates)
    )
    client = get_client()
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "You rerank retrieved passages for a mainframe knowledge search. "
                    "Reply with a comma-separated list of passage indices, most relevant first. "
                    "Use each index at most once. No other text."
                ),
            },
            {
                "role": "user",
                "content": f"Question: {question}\n\nPassages:\n{numbered}",
            },
        ],
    )
    raw = (response.choices[0].message.content or "").strip()
    order = [int(x) for x in re.findall(r"\d+", raw)]
    seen: set[int] = set()
    ranked: list[dict] = []
    for i in order:
        if 0 <= i < len(candidates) and i not in seen:
            seen.add(i)
            ranked.append(candidates[i])
    ranked.extend(c for i, c in enumerate(candidates) if i not in seen)
    return ranked[:k]


def main() -> None:
    docs = load_corpus()
    print(f"corpus: {len(docs)} documents · model: {MODEL}")
    lines = ["# W5 Rerank Benchmark", "",
             f"Questions: {len(QUESTIONS)} · retrieve {CANDIDATES} · k = {K}", "",
             "| Chunking | Retriever | Hit rate | Recall@k | MRR |",
             "|----------|-----------|----------|----------|-----|"]
    for strategy in ["fixed", "structure"]:
        index = Index(chunk_corpus(docs, strategy))
        for method in ["hybrid"]:
            baseline = {q["question"]: search(index, q["question"], method, k=K)
                        for q in QUESTIONS}
            reranked = {
                q["question"]: rerank(
                    q["question"],
                    search(index, q["question"], method, k=CANDIDATES),
                    k=K,
                )
                for q in QUESTIONS
            }
            for label, run in ((method, baseline), (f"{method}+rerank", reranked)):
                m = evaluate(run, QUESTIONS, docs, k=K)
                lines.append(
                    f"| {strategy} | {label} | {m['hit_rate']} | {m['recall']} | {m['mrr']} |")
    table = "\n".join(lines)
    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    (out / "rerank_benchmark.md").write_text(table + "\n", encoding="utf-8")
    print("\n" + table)
    print("\nwrote results/rerank_benchmark.md")


if __name__ == "__main__":
    main()
