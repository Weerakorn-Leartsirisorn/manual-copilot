"""All settings come from environment variables (never hard-code API keys)."""
import os
from pathlib import Path

# Load a .env file next to the project root if it exists (simple KEY=VALUE lines).
_env = Path(__file__).resolve().parent.parent / ".env"
if _env.exists():
    for line in _env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

# Chat model served by vLLM on AMD Developer Cloud
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:8000/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "Qwen/Qwen2.5-7B-Instruct")

# Embedding model served by a second vLLM process on the same AMD GPU
EMBED_BASE_URL = os.getenv("EMBED_BASE_URL", "http://localhost:8001/v1")
EMBED_MODEL = os.getenv("EMBED_MODEL", "BAAI/bge-m3")

API_KEY = os.getenv("VLLM_API_KEY", "change-me-please")

# Retrieval settings
CHUNK_CHARS = int(os.getenv("CHUNK_CHARS", "900"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))
TOP_K = int(os.getenv("TOP_K", "4"))
# Below this similarity we say "not in the manual" and escalate to a person.
MIN_SCORE = float(os.getenv("MIN_SCORE", "0.45"))

INDEX_DIR = os.getenv("INDEX_DIR", "index_store")
