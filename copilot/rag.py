"""Retrieve the right manual pages, then ask the AMD-hosted LLM to answer from them only."""
import time
from dataclasses import dataclass, field

from openai import OpenAI

from . import config
from .index import VectorIndex

SYSTEM_PROMPT = """You are a maintenance assistant for factory technicians.
Answer ONLY from the manual excerpts provided. Rules:
1. Reply in the same language as the question (Thai question -> Thai answer).
2. Give short numbered steps a technician can follow on the shop floor.
3. Cite the page after each fact, like [HP-200_manual.pdf p.4].
4. If the excerpts mention a safety warning (lockout/tagout, pressure release,
   protective equipment), put it FIRST, starting with "⚠️".
5. If the excerpts do not contain the answer, say exactly that and recommend
   asking a supervisor. Never invent part numbers, values or procedures."""


@dataclass
class Answer:
    text: str
    sources: list[dict] = field(default_factory=list)
    confidence: float = 0.0
    escalate: bool = False
    seconds: float = 0.0


def llm_client() -> OpenAI:
    return OpenAI(base_url=config.LLM_BASE_URL, api_key=config.API_KEY)


def _context(hits) -> str:
    return "\n\n".join(
        f"[{c.source} p.{c.page}]\n{c.text}" for c, _ in hits
    )


def answer(question: str, index: VectorIndex, history: list[dict] | None = None,
           llm: OpenAI | None = None, embedder: OpenAI | None = None) -> Answer:
    t0 = time.time()
    hits = index.search(question, config.TOP_K, embedder)
    best = hits[0][1] if hits else 0.0
    sources = [{"source": c.source, "page": c.page, "score": round(s, 3),
                "preview": c.text[:220]} for c, s in hits]

    # Human-in-the-loop: weak match -> don't guess, hand over to a person.
    if not hits or best < config.MIN_SCORE:
        return Answer(
            text=("I couldn't find this in the uploaded manuals, so I won't guess. "
                  "Please check with a supervisor or the machine vendor.\n\n"
                  "ไม่พบข้อมูลนี้ในคู่มือที่อัปโหลด จึงไม่ขอเดาคำตอบ "
                  "กรุณาสอบถามหัวหน้างานหรือผู้ผลิตเครื่อง"),
            sources=sources, confidence=best, escalate=True, seconds=time.time() - t0)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for turn in (history or [])[-4:]:  # a little memory for follow-up questions
        messages.append({"role": turn["role"], "content": turn["content"]})
    messages.append({"role": "user",
                     "content": f"Manual excerpts:\n{_context(hits)}\n\nQuestion: {question}"})

    resp = (llm or llm_client()).chat.completions.create(
        model=config.LLM_MODEL, messages=messages, temperature=0.1, max_tokens=700)
    return Answer(text=resp.choices[0].message.content.strip(), sources=sources,
                  confidence=best, escalate=False, seconds=time.time() - t0)
