# 🔧 Manual Copilot — ask your machine manuals, get cited answers

> Built for the **AMD Developer Hackathon: ACT III** · Track 1: *Intelligent Industry*
> All AI inference runs on an **AMD Instinct™ MI300X** GPU (AMD Developer Cloud, ROCm + vLLM).

## The problem
When a press stops with an error code at 3 a.m., the technician has to dig through a
200-page PDF manual — often in a language they don't read well — while production is down.
The answer is in the manual; finding it is the slow part.

## What it does
- 📄 Upload the PDF manuals for your machines.
- 💬 Ask in plain language — **English or Thai** — e.g. *"The display shows E-07, what do I do?"*
- 📌 Get numbered steps with **page citations** (`[HP-200_manual.pdf p.4]`) so the technician can verify.
- ⚠️ Safety warnings (lockout/tagout, pressure release) are always shown **first**.
- 🔴 If the manual doesn't cover the question, it **refuses to guess** and escalates to a supervisor.

**Who uses it:** maintenance technicians and line operators.
**What it improves:** time to find the right procedure → shorter downtime, fewer unsafe shortcuts.

<!-- TODO: add a screenshot or GIF of the app here: ![demo](docs/demo.gif) -->

## Architecture

```
 PDF manuals ──► pypdf: split into chunks (keeps page numbers)
                     │
                     ▼
        ┌──────── AMD Instinct MI300X (AMD Developer Cloud, ROCm) ────────┐
        │  vLLM :8001  BAAI/bge-m3        → embeddings (multilingual)     │
        │  vLLM :8000  Qwen2.5-7B-Instruct → grounded answer + citations   │
        └──────────────────────────────────────────────────────────────────┘
                     ▲
 Question ──► vector search (numpy cosine) ──► top-4 pages ──► LLM ──► answer
                     │
                     └── best match < MIN_SCORE?  → "not in manual, ask a supervisor"
```

Both the embedding model and the chat model are served from **one MI300X** (192 GB HBM)
as two vLLM processes. The web app itself is lightweight and talks to them over the
OpenAI-compatible API.

## Run it

### 1. Start the models on AMD Developer Cloud
1. Create a GPU Droplet: **1× MI300X**, image **vLLM Quick Start**.
2. SSH in, copy the `amd/` folder over, then:
   ```bash
   docker exec -it rocm /bin/bash
   export VLLM_API_KEY=pick-a-secret
   bash amd/serve_models.sh
   bash amd/check_endpoints.sh      # when both logs say "startup complete"
   ```
> 💸 Destroy the droplet when you're not using it — credits are billed per hour.

### 2. Run the app (laptop or the droplet)
```bash
pip install -r requirements.txt
cp .env.example .env               # put your droplet IP + API key in .env
python scripts/make_sample_manual.py
python app.py                      # open http://localhost:7860
```
Or with Docker: `docker build -t manual-copilot . && docker run -p 7860:7860 --env-file .env manual-copilot`

### Develop without a GPU
`python scripts/mock_server.py` starts a fake OpenAI-compatible server on `:9000`
(dumb answers, but the whole UI works). Point `LLM_BASE_URL` and `EMBED_BASE_URL` at
`http://localhost:9000/v1`.

## Project layout
```
amd/serve_models.sh        start chat + embedding models with vLLM on ROCm
amd/check_endpoints.sh     health check for both endpoints
copilot/ingest.py          PDF → page-aware chunks
copilot/index.py           embeddings (AMD) + numpy vector search, save/load
copilot/rag.py             retrieval, prompt, confidence gate, answer
app.py                     Gradio UI
scripts/make_sample_manual.py   fictional demo manual (HP-200 press)
scripts/mock_server.py     offline fake model server for development
```

## Responsible design
- Answers only from the uploaded manuals; every fact is cited to a page.
- Confidence gate (`MIN_SCORE`) — weak retrieval means *no answer* plus escalation.
- Never invents part numbers or torque values (enforced in the system prompt, verifiable via citations).
- The sample manual is fictional; no vendor content is included.

## Results
<!-- TODO: fill in after testing on the MI300X -->
| Metric | Value |
|---|---|
| Avg. answer time on MI300X | _x.x s_ |
| Correct page in top-4 (20 test questions) | _xx / 20_ |
| Out-of-scope questions correctly refused | _x / 5_ |

## Roadmap
- Maintenance-log search (past repairs for the same error code)
- Scanned-PDF OCR, images from the manual in answers
- Voice input for hands-busy technicians

## License
MIT
