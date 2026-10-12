"""Read PDF manuals and cut them into small chunks that remember their page."""
from dataclasses import dataclass, asdict
from pathlib import Path

from pypdf import PdfReader

from . import config


@dataclass
class Chunk:
    text: str
    source: str  # file name, e.g. "HP-200_manual.pdf"
    page: int    # 1-based page number, shown to the technician

    def to_dict(self):
        return asdict(self)


def _split(text: str, size: int, overlap: int) -> list[str]:
    """Split text into pieces of ~size characters, breaking on blank lines when possible."""
    text = text.strip()
    if len(text) <= size:
        return [text] if text else []
    pieces, start = [], 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            # prefer to cut at a paragraph or sentence boundary
            for sep in ("\n\n", "\n", ". "):
                cut = text.rfind(sep, start + size // 2, end)
                if cut != -1:
                    end = cut + len(sep)
                    break
        pieces.append(text[start:end].strip())
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return [p for p in pieces if p]


def load_pdf(path: str | Path) -> list[Chunk]:
    path = Path(path)
    reader = PdfReader(str(path))
    chunks: list[Chunk] = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        for piece in _split(text, config.CHUNK_CHARS, config.CHUNK_OVERLAP):
            chunks.append(Chunk(text=piece, source=path.name, page=i))
    return chunks
