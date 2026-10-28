"""Ask the search service one question; print passages with provenance.
No answer generation — W5 is retrieval only. If the right passage is
not retrieved, no answer layer can rescue it.

Usage (from the project root):
  python scripts/ask.py "What does file status 39 mean?"
  python scripts/ask.py "Which job loads transactions?" --method bm25 --chunking fixed
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv()

from src.chunking import chunk_corpus  # noqa: E402
from src.corpus import load_corpus  # noqa: E402
from src.index import Index  # noqa: E402
from src.search import search  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("question")
    ap.add_argument("--method", default="hybrid",
                    choices=["vector", "bm25", "hybrid"])
    ap.add_argument("--chunking", default="structure",
                    choices=["fixed", "structure"])
    ap.add_argument("--k", type=int, default=5)
    a = ap.parse_args()

    docs = load_corpus()
    index = Index(chunk_corpus(docs, a.chunking))
    for i, r in enumerate(search(index, a.question, a.method, k=a.k), 1):
        print(f"\n[{i}] {r['file']} :: {r['section']} :: score {r['score']}")
        print("    " + " ".join(r["text"].split())[:300])


if __name__ == "__main__":
    main()
