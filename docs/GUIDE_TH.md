# คู่มือเริ่มต้น (ภาษาไทย) — Manual Copilot

## วันที่ 1: ลองบนเครื่องตัวเองก่อน (ไม่เสียเครดิต GPU)
```bash
pip install -r requirements.txt
python scripts/make_sample_manual.py        # สร้างคู่มือตัวอย่าง sample_data/HP-200_manual.pdf
python scripts/mock_server.py               # หน้าต่าง terminal ที่ 1 (โมเดลปลอม)
```
เปิด terminal ที่ 2:
```bash
# Windows PowerShell:
#   $env:LLM_BASE_URL="http://localhost:9000/v1"; $env:EMBED_BASE_URL="http://localhost:9000/v1"; $env:MIN_SCORE="0.2"; python app.py
LLM_BASE_URL=http://localhost:9000/v1 EMBED_BASE_URL=http://localhost:9000/v1 MIN_SCORE=0.2 python app.py
```
เปิด http://localhost:7860 → กด "Load sample manual" → ลองถามคำถามตัวอย่าง
(คำตอบจะยังไม่ฉลาด เพราะเป็นโมเดลปลอม แค่เช็กว่าระบบทำงาน)

## วันที่ 1–2: รันโมเดลจริงบน AMD
1. เข้า AMD Developer Cloud → สร้าง GPU Droplet: **MI300X 1 ตัว**, image **vLLM Quick Start**
2. คัดลอกโฟลเดอร์ `amd/` ขึ้นเครื่อง (เช่น `scp -r amd root@IP:~/`)
3. SSH เข้าเครื่อง แล้วรัน:
   ```bash
   docker exec -it rocm /bin/bash
   export VLLM_API_KEY=ตั้งรหัสลับเอง
   bash amd/serve_models.sh
   tail -f /tmp/vllm_chat.log      # รอจนขึ้น "Application startup complete"
   bash amd/check_endpoints.sh     # ต้องได้คำตอบจากโมเดล + ตัวเลข 1024
   ```
4. บนเครื่องตัวเอง: `cp .env.example .env` แล้วแก้ IP กับ API key ให้ตรง → `python app.py`

> ⚠️ ถ้า `amd/` หาไม่เจอหลัง `docker exec` แปลว่าไฟล์อยู่นอก container ให้คัดลอกเข้าไปด้วย
> `docker cp amd rocm:/root/` แล้วค่อย `cd /root`
>
> 💸 ปิด (Destroy) droplet ทุกครั้งที่เลิกใช้ ไม่งั้นเครดิต $100 หมดไว

## วันที่ 3: ปรับให้ดีขึ้น
- **ตั้งค่า MIN_SCORE**: ถามคำถามที่มีในคู่มือ 5 ข้อ กับคำถามนอกเรื่อง 5 ข้อ
  ดูค่า "best match" ที่แอปแสดง แล้วตั้ง MIN_SCORE ไว้ระหว่างสองกลุ่ม
- ลองใช้คู่มือจริงที่เปิดเผยสาธารณะ (ตรวจสอบสิทธิ์ก่อนใส่ใน GitHub)
- ทำชุดทดสอบ 20 คำถาม แล้วนับว่าหน้าที่ถูกอยู่ใน top-4 กี่ข้อ → ใส่ในตาราง Results ของ README

## วันที่ 4–5: งานส่ง
- อัด GIF/วิดีโอ 2–3 นาที: ปัญหา → อัปโหลดคู่มือ → ถาม E-07 (ไทย+อังกฤษ) → เห็นเลขหน้า → ถามนอกเรื่องแล้วระบบไม่เดา
- พูดให้ชัดว่า "โมเดลทั้งสองตัวรันบน AMD MI300X ผ่าน ROCm + vLLM"
- ทำ GitHub repo สาธารณะ ห้าม commit ไฟล์ `.env`
