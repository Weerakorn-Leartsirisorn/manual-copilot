"""Manual Copilot - web UI (Gradio).

Run:  python app.py   then open http://localhost:7860
"""
from pathlib import Path

import gradio as gr

from copilot import config
from copilot.index import VectorIndex
from copilot.ingest import load_pdf
from copilot.rag import answer

SAMPLE_DIR = Path(__file__).parent / "sample_data"
INDEX = VectorIndex.load()


def _status() -> str:
    if len(INDEX) == 0:
        return "📭 No manuals loaded yet. Upload a PDF or load the sample manual."
    files = "\n".join(f"- {s}" for s in INDEX.sources())
    return f"📚 **{len(INDEX)} chunks indexed** from:\n{files}"


def add_pdfs(files):
    for f in files or []:
        path = Path(f if isinstance(f, str) else f.name)
        INDEX.remove_source(path.name)          # re-upload replaces the old copy
        INDEX.add(load_pdf(path))
    INDEX.save()
    return _status()


def load_sample():
    return add_pdfs([str(p) for p in sorted(SAMPLE_DIR.glob("*.pdf"))])


def clear_index():
    global INDEX
    INDEX = VectorIndex()
    INDEX.save()
    return _status()


def _text(content) -> str:
    """Gradio messages can carry strings or lists of parts; keep only the text."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(p.get("text", "") if isinstance(p, dict) else str(p) for p in content)
    return str(content)


def chat(question, history):
    history = history or []
    if not question.strip():
        return "", history, gr.update()
    if len(INDEX) == 0:
        reply = "Please load a manual first (left panel)."
        return "", history + [{"role": "user", "content": question},
                              {"role": "assistant", "content": reply}], gr.update()

    past = [{"role": m["role"], "content": _text(m["content"])} for m in history]
    try:
        ans = answer(question, INDEX, history=past)
    except Exception as e:  # endpoint down, wrong key, etc.
        reply = f"❌ Could not reach the model server: `{e}`\nCheck LLM_BASE_URL / EMBED_BASE_URL."
        return "", history + [{"role": "user", "content": question},
                              {"role": "assistant", "content": reply}], gr.update()

    badge = "🔴 Low confidence → escalate to a person" if ans.escalate else "🟢 Answer grounded in the manual"
    sources_md = "\n".join(
        f"**{i}. {s['source']} — page {s['page']}** (match {s['score']:.2f})\n> {s['preview']}…\n"
        for i, s in enumerate(ans.sources, 1))
    details = (f"{badge}  \n⏱️ {ans.seconds:.1f}s on AMD Instinct GPU · best match {ans.confidence:.2f}"
               f"\n\n### Sources\n{sources_md}")
    return "", history + [{"role": "user", "content": question},
                          {"role": "assistant", "content": ans.text}], details


EXAMPLES = [
    "The display shows E-07. What should I do?",
    "เครื่องแสดง E-07 ต้องทำอย่างไร",
    "How often should I change the hydraulic oil filter?",
    "ก่อนเปลี่ยนแม่พิมพ์ต้องทำขั้นตอนความปลอดภัยอะไรบ้าง",
    "What is the warranty on the coffee machine?",  # not in manual -> escalation demo
]

with gr.Blocks(title="Manual Copilot") as demo:
    gr.Markdown("# 🔧 Manual Copilot\nAsk your machine manuals in plain language — "
                "answers cite the page, and say *I don't know* when the manual doesn't. "
                "Models run on **AMD Instinct MI300X** via ROCm + vLLM.")
    with gr.Row():
        with gr.Column(scale=1):
            status = gr.Markdown(_status())
            uploads = gr.File(label="Upload PDF manuals", file_count="multiple", file_types=[".pdf"])
            with gr.Row():
                sample_btn = gr.Button("Load sample manual")
                clear_btn = gr.Button("Clear", variant="stop")
        with gr.Column(scale=2):
            bot = gr.Chatbot(height=460, label="Technician chat")
            q = gr.Textbox(placeholder="e.g. The display shows E-07. What should I do?",
                           show_label=False)
            gr.Examples(EXAMPLES, inputs=q)
        with gr.Column(scale=1):
            details = gr.Markdown("Sources will appear here.")

    uploads.upload(add_pdfs, uploads, status)
    sample_btn.click(load_sample, None, status)
    clear_btn.click(clear_index, None, status)
    q.submit(chat, [q, bot], [q, bot, details])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=int(__import__("os").getenv("PORT", "7860")))
