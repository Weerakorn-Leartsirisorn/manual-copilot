# Learnings — Manual Copilot

บันทึกสิ่งที่ได้เรียนรู้ในแต่ละ phase ของการทำโปรเจกต์ (AMD Developer Hackathon: ACT III)

---

## Phase 1 — Local setup (12 ต.ค. 2026)

### สิ่งที่ทำ
- `git init` + commit แรก (เช็กแล้วว่า `.gitignore` กัน `.env`, `.venv/`, `index_store/`)
- สร้าง virtual env `.venv` แล้ว `pip install -r requirements.txt`
- รัน `scripts/mock_server.py` (:9000) + `app.py` (:7860) แล้วลองใช้จริงในเบราว์เซอร์

### ผลลัพธ์
| คำถาม | best match | ผล |
|---|---|---|
| The display shows E-07. What should I do? | 0.28 | 🟢 ตอบ + อ้าง `[HP-200_manual.pdf p.4]` ถูกหน้า |
| What is the warranty on the coffee machine? (นอกคู่มือ) | 0.44 | 🟢 ตอบ ❌ ควรจะ escalate |

### สิ่งที่ได้เรียนรู้
1. **Virtual env (`.venv`)** = กล่องแยก package ของโปรเจกต์นี้ ไม่ปนกับ Python ของเครื่อง
2. **Mock server** ช่วยให้พัฒนา UI ได้โดยไม่เสียเงินค่า GPU — เพราะแอปคุยผ่าน OpenAI-compatible API แค่เปลี่ยน `LLM_BASE_URL` ก็สลับไปโมเดลจริงได้
3. **Mock embedding ≠ ความหมาย** — mock แค่นับคำ (bag-of-words) คำทั่วไปอย่าง "what / is / the" เลยดันคะแนนคำถามนอกเรื่องให้สูงกว่าคำถามจริง
   → confidence gate จะเชื่อถือได้ก็ต่อเมื่อใช้ embedding จริง (bge-m3) และ **calibrate `MIN_SCORE`** (Phase 3)
4. ตัวเลขที่ "ดูดี" ใน UI ไม่ได้แปลว่าระบบถูก — ต้องทดสอบทั้งเคสที่ควรตอบ และเคสที่ **ไม่ควร** ตอบ

### ข้อสังเกตไว้ทำต่อ
- UI แสดง "⏱️ … on AMD Instinct GPU" แม้กำลังใช้ mock → ควรแสดงตาม endpoint จริง (Phase 4 ตอนทำ badge)
