"""A tiny vector index: embeddings come from the AMD-hosted model, search is numpy."""
import json
from pathlib import Path

import numpy as np
from openai import OpenAI

from . import config
from .ingest import Chunk


def embed_client() -> OpenAI:
    return OpenAI(base_url=config.EMBED_BASE_URL, api_key=config.API_KEY)


def embed(texts: list[str], client: OpenAI | None = None, batch: int = 32) -> np.ndarray:
    """Call the embedding endpoint (runs on the AMD GPU) and return unit vectors."""
    client = client or embed_client()
    vectors = []
    for i in range(0, len(texts), batch):
        resp = client.embeddings.create(model=config.EMBED_MODEL, input=texts[i:i + batch])
        vectors.extend(d.embedding for d in resp.data)
    arr = np.asarray(vectors, dtype=np.float32)
    arr /= np.linalg.norm(arr, axis=1, keepdims=True) + 1e-12
    return arr


class VectorIndex:
    def __init__(self):
        self.chunks: list[Chunk] = []
        self.vectors = np.zeros((0, 0), dtype=np.float32)

    def __len__(self):
        return len(self.chunks)

    def sources(self) -> list[str]:
        return sorted({c.source for c in self.chunks})

    def add(self, chunks: list[Chunk], client: OpenAI | None = None):
        if not chunks:
            return
        new = embed([c.text for c in chunks], client)
        self.vectors = new if len(self) == 0 else np.vstack([self.vectors, new])
        self.chunks.extend(chunks)

    def remove_source(self, source: str):
        keep = [i for i, c in enumerate(self.chunks) if c.source != source]
        self.chunks = [self.chunks[i] for i in keep]
        self.vectors = self.vectors[keep] if keep else np.zeros((0, 0), dtype=np.float32)

    def search(self, query: str, k: int, client: OpenAI | None = None) -> list[tuple[Chunk, float]]:
        if len(self) == 0:
            return []
        q = embed([query], client)[0]
        scores = self.vectors @ q
        top = np.argsort(-scores)[:k]
        return [(self.chunks[i], float(scores[i])) for i in top]

    # --- save / load so you don't re-embed every restart ---
    def save(self, folder: str | Path = config.INDEX_DIR):
        folder = Path(folder)
        folder.mkdir(parents=True, exist_ok=True)
        np.save(folder / "vectors.npy", self.vectors)
        (folder / "chunks.json").write_text(
            json.dumps([c.to_dict() for c in self.chunks], ensure_ascii=False), encoding="utf-8")

    @classmethod
    def load(cls, folder: str | Path = config.INDEX_DIR) -> "VectorIndex":
        folder = Path(folder)
        idx = cls()
        if (folder / "chunks.json").exists():
            idx.chunks = [Chunk(**d) for d in json.loads((folder / "chunks.json").read_text(encoding="utf-8"))]
            idx.vectors = np.load(folder / "vectors.npy")
        return idx
