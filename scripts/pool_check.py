import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv()

from src.chunking import chunk_corpus
from src.corpus import load_corpus
from src.index import Index
from src.metrics import evaluate
from src.search import search

SUSPECTS = [
    "What caused the S0C7 abend in March 2025?",
    "What time does the nightly batch start?",
]

docs = load_corpus()
qs = {q["question"]: q for q in json.loads(
    Path("evals/questions.json").read_text(encoding="utf-8"))}
index = Index(chunk_corpus(docs, "structure"))
for text in SUSPECTS:
    pool = search(index, text, "hybrid", k=10)
    pq = evaluate({text: pool}, [qs[text]], docs, k=10)["per_question"][0]
    verdict = ("ABSENT from pool -> recall/depth failure"
               if pq["found"] == 0 else
               f"in pool, first relevant at rank {pq['first_rank']} "
               "-> reranker judgment if unrescued")
    print(f"{text}\n  {verdict}")
