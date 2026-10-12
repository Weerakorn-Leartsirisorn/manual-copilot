# Manual Copilot — Project Brief

> Context file for Claude Code. Place it in the repo root; Claude Code reads it automatically.

## How to work with me
- I'm a **beginner**. Explain what you're doing in short, plain Thai (ตอบเป็นภาษาไทย), keep code and commit messages in English.
- Prefer small, working steps over big rewrites. Run the app/tests after each change.
- Never commit `.env` or API keys. Never hard-code secrets — use environment variables.

## The hackathon
- **Event:** AMD Developer Hackathon: ACT III (lablab.ai)
- **Online build:** 12–18 October 2026 → **submission deadline: 18 Oct 2026**
- **Track:** 1 — *Intelligent Industry* (idea from the brief: help technicians search manuals and maintenance records)
- **Hard requirement:** a meaningful part of the working product must run on AMD (we use AMD Developer Cloud, MI300X, ROCm + vLLM). This must be visible in the demo.
- **Judging criteria:** Application of Technology · Presentation · Business Value · Originality
- **Submission:** title, short + long description, tech tags, cover image, demo video, slide deck, **public GitHub repo**, app URL. Must be original and MIT-licensed.
- **My goal:** a clean, working project for my portfolio. Winning is a bonus, so favor polish and a great README over extra features.

## The idea
**Problem:** When a machine stops with an error code, technicians dig through long PDF manuals (often not in their language) while production is down.

**Product:** Upload machine manuals (PDF) → ask in plain English or Thai → get step-by-step answers **with page citations**.

**Key behaviors (keep these — they are the selling points):**
1. Every fact cites a page, e.g. `[HP-200_manual.pdf p.4]`.
2. Safety warnings (lockout/tagout, pressure release, PPE) are shown **first** with ⚠️.
3. Answers in the same language as the question (Thai ↔ English).
4. **Confidence gate:** if the best retrieval score < `MIN_SCORE`, do not call the LLM; reply "not in the manual, ask a supervisor" (human-in-the-loop).
5. Never invent part numbers, torque values or procedures.

**User:** maintenance technicians, line operators. **Value:** less time to find the right procedure → shorter downtime, fewer unsafe shortcuts.

## Architecture
```
PDF manuals ─► pypdf: page-aware chunks (~900 chars, 150 overlap)
                  │
   ┌──── AMD Instinct MI300X · AMD Developer Cloud · ROCm ────┐
   │ vLLM :8001  BAAI/bge-m3            → embeddings           │
   │ vLLM :8000  Qwen/Qwen2.5-7B-Instruct → grounded answer     │
   └────────────────────────────────────────────────────────────┘
                  ▲
Question ─► numpy cosine search ─► top-4 chunks ─► LLM ─► answer + sources
                  └─ best score < MIN_SCORE → escalate, no LLM call
```
- Both models share one MI300X as two vLLM processes (`--gpu-memory-utilization` 0.45 / 0.15).
- The app talks to them through the OpenAI-compatible API (`openai` Python client).
- Vector store = numpy arrays saved to `index_store/` (no database on purpose — keep it simple).

## File structure
```
manual-copilot/
├── CLAUDE.md                  this file
├── README.md                  portfolio-facing README (English)
├── LICENSE                    MIT
├── requirements.txt
├── Dockerfile                 app container (no GPU needed; models are remote)
├── .env.example               copy to .env (gitignored)
├── app.py                     Gradio UI: upload PDFs, chat, sources panel
├── copilot/
│   ├── config.py              env-var settings + tiny .env loader
│   ├── ingest.py              PDF → Chunk(text, source, page)
│   ├── index.py               embed() via AMD endpoint, VectorIndex (add/remove/search/save/load)
│   └── rag.py                 SYSTEM_PROMPT, confidence gate, answer() → Answer
├── amd/
│   ├── serve_models.sh        start both vLLM servers (run inside `docker exec -it rocm bash`)
│   └── check_endpoints.sh     curl health check for :8000 and :8001
├── scripts/
│   ├── make_sample_manual.py  builds fictional sample_data/HP-200_manual.pdf (7 pages, error codes E-01…E-21)
│   └── mock_server.py         fake OpenAI-compatible server on :9000 for dev without GPU credits
├── sample_data/HP-200_manual.pdf
└── docs/GUIDE_TH.md           step-by-step guide in Thai
```

## Commands
```bash
pip install -r requirements.txt
python scripts/make_sample_manual.py

# Dev without GPU (two terminals)
python scripts/mock_server.py
LLM_BASE_URL=http://localhost:9000/v1 EMBED_BASE_URL=http://localhost:9000/v1 MIN_SCORE=0.2 python app.py

# Real models: fill .env with droplet IP + VLLM_API_KEY, then
python app.py            # http://localhost:7860
```

## Environment variables
| Var | Default | Notes |
|---|---|---|
| `LLM_BASE_URL` | `http://localhost:8000/v1` | vLLM chat endpoint on AMD |
| `LLM_MODEL` | `Qwen/Qwen2.5-7B-Instruct` | |
| `EMBED_BASE_URL` | `http://localhost:8001/v1` | vLLM embedding endpoint on AMD |
| `EMBED_MODEL` | `BAAI/bge-m3` | multilingual, works for Thai |
| `VLLM_API_KEY` | `change-me-please` | must match `serve_models.sh` |
| `MIN_SCORE` | `0.45` | **not calibrated yet** for bge-m3 |
| `TOP_K` / `CHUNK_CHARS` / `CHUNK_OVERLAP` | 4 / 900 / 150 | |
| `INDEX_DIR` | `index_store` | |

## Current status
- ✅ Full pipeline works end-to-end against `mock_server.py` (ingest → index → search → answer → Gradio UI).
- ⚠️ **Not yet tested on a real MI300X.** `amd/serve_models.sh` may need tweaks for the vLLM version on the droplet (e.g. `--task embed` / `--runner pooling` for bge-m3).
- ⚠️ `MIN_SCORE` needs calibration with real embeddings.
- ⚠️ No automated tests yet.

## Plan / TODO
**Day 1–2 — get it running on AMD**
- [ ] Create droplet (1× MI300X, "vLLM Quick Start" image), run `serve_models.sh`, pass `check_endpoints.sh`
- [ ] Point `.env` at the droplet and test the app with the sample manual

**Day 3 — quality**
- [ ] Calibrate `MIN_SCORE`: 10 in-manual vs 5 out-of-scope questions, set threshold between the two groups
- [ ] `scripts/eval.py`: ~20 Q&A pairs with the expected page → report "correct page in top-4" and avg latency
- [ ] Add `tests/` with pytest for `ingest._split` and `VectorIndex` (use mock embeddings)

**Day 4 — nice-to-have (only if the above is done)**
- [ ] Streaming answers in the UI
- [ ] Show a "Running on AMD Instinct MI300X" badge with the measured latency
- [ ] Maintenance-log CSV search (past fixes for the same error code)

**Day 5–6 — submission**
- [ ] Fill the Results table in README with real numbers; add screenshot/GIF
- [ ] Demo video 2–3 min: problem → upload → ask E-07 (Thai + English) → citations → out-of-scope question gets refused
- [ ] Slide deck (problem, user, solution, AMD architecture, results, roadmap)
- [ ] Public GitHub repo, deploy app (e.g. on the droplet or Hugging Face Spaces) for the app URL
- [ ] Destroy the droplet when idle to save credits ($100 free)

## Out of scope (don't build unless asked)
User accounts, databases, fine-tuning, OCR for scanned PDFs, mobile apps.
