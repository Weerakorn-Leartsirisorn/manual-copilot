"""Fake OpenAI-compatible server for building the UI WITHOUT spending GPU credits.

It is NOT smart: embeddings are word-hash vectors and the "LLM" just quotes the
best excerpt. Use it to develop the app, then switch to the real AMD endpoints.

    python scripts/mock_server.py            # listens on :9000
    LLM_BASE_URL=http://localhost:9000/v1 EMBED_BASE_URL=http://localhost:9000/v1 python app.py
"""
import hashlib
import re
import time

import numpy as np
import uvicorn
from fastapi import FastAPI, Request

app = FastAPI()
DIM = 512


def fake_embed(text: str) -> list[float]:
    v = np.zeros(DIM, dtype=np.float32)
    for w in re.findall(r"[\w-]+", text.lower()):
        v[int(hashlib.md5(w.encode()).hexdigest(), 16) % DIM] += 1.0
    n = np.linalg.norm(v)
    return (v / n if n else v).tolist()


@app.post("/v1/embeddings")
async def embeddings(req: Request):
    body = await req.json()
    inputs = body["input"] if isinstance(body["input"], list) else [body["input"]]
    return {"object": "list", "model": body.get("model", "mock"),
            "data": [{"object": "embedding", "index": i, "embedding": fake_embed(t)}
                     for i, t in enumerate(inputs)],
            "usage": {"prompt_tokens": 0, "total_tokens": 0}}


@app.post("/v1/chat/completions")
async def chat(req: Request):
    body = await req.json()
    last = body["messages"][-1]["content"]
    first_excerpt = last.split("\n\n")[0].replace("Manual excerpts:\n", "")
    text = f"(mock model) Based on the manual:\n\n{first_excerpt[:600]}"
    return {"id": "mock", "object": "chat.completion", "created": int(time.time()),
            "model": body.get("model", "mock"),
            "choices": [{"index": 0, "finish_reason": "stop",
                         "message": {"role": "assistant", "content": text}}],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
