"""Chunking strategies, deliberately different in kind.

fixed:         character windows with overlap — blind to document structure.
structure:     split on the document's own boundaries (markdown headings,
               COBOL 01-levels) — one chunk per section, sub-splitting only
               when a section is very long.
structure_ctx: same spans as structure, but each chunk's indexed text is
               prefixed with the document preamble (title/header, decoration
               stripped) so later sections still carry incident ids, abend
               codes, and dates. start/end stay on the original span so
               span-overlap judging remains fair.

W5's first question: does respecting structure beat blind windows on
mainframe text, where a record layout is a hierarchy and a window can
cut a field definition in half?
"""
import re
from dataclasses import dataclass

from .corpus import Doc


@dataclass
class Chunk:
    file: str
    section: str
    start: int
    end: int
    text: str


def chunk_fixed(doc: Doc, size: int = 500, overlap: int = 50) -> list[Chunk]:
    chunks: list[Chunk] = []
    start, n = 0, len(doc.text)
    while start < n:
        end = min(start + size, n)
        chunks.append(Chunk(doc.file, doc.section_at(start), start, end,
                            doc.text[start:end]))
        if end == n:
            break
        start = end - overlap
    return chunks


def chunk_structure(doc: Doc, max_chars: int = 1200) -> list[Chunk]:
    chunks: list[Chunk] = []
    for s in doc.sections:
        text = doc.text[s.start:s.end]
        if len(text) <= max_chars:
            chunks.append(Chunk(doc.file, s.name, s.start, s.end, text))
        else:
            off = 0
            while off < len(text):
                piece = text[off:off + max_chars]
                chunks.append(Chunk(doc.file, s.name, s.start + off,
                                    s.start + off + len(piece), piece))
                off += max_chars
    return chunks


_PREAMBLE_NAMES = {"(title)", "(header)"}
_PREAMBLE_DECORATION = re.compile(r"[#*=]")
_PREAMBLE_CAP = 150


def _preamble(doc: Doc, cap: int = _PREAMBLE_CAP) -> str:
    """Title/header text with #/*/= stripped, whitespace collapsed, ~cap chars."""
    section = next((s for s in doc.sections if s.name in _PREAMBLE_NAMES), None)
    if section is None:
        return ""
    stripped = _PREAMBLE_DECORATION.sub("", doc.text[section.start:section.end])
    compact = " ".join(stripped.split())
    if len(compact) <= cap:
        return compact
    cut = compact[:cap].rsplit(" ", 1)[0]
    return cut or compact[:cap]


def chunk_structure_ctx(doc: Doc, max_chars: int = 1200) -> list[Chunk]:
    prefix = _preamble(doc)
    chunks = chunk_structure(doc, max_chars)
    if not prefix:
        return chunks
    return [Chunk(c.file, c.section, c.start, c.end, f"{prefix}\n{c.text}")
            for c in chunks]


STRATEGIES = {
    "fixed": chunk_fixed,
    "structure": chunk_structure,
    "structure_ctx": chunk_structure_ctx,
}


def chunk_corpus(docs: list[Doc], strategy: str) -> list[Chunk]:
    fn = STRATEGIES[strategy]
    return [c for d in docs for c in fn(d)]
