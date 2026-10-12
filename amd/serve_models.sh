#!/usr/bin/env bash
# ------------------------------------------------------------------
# Start two vLLM servers on ONE AMD Instinct MI300X GPU (ROCm):
#   :8000  chat model       (answers the technician's question)
#   :8001  embedding model  (turns manual pages into vectors for search)
#
# Where to run this:
#   AMD Developer Cloud -> GPU Droplet -> image "vLLM Quick Start"
#   then enter the ready-made container:   docker exec -it rocm /bin/bash
#   and run:                               bash serve_models.sh
#
# Both models are small, so they share the 192 GB of the MI300X easily.
# ------------------------------------------------------------------
set -euo pipefail

CHAT_MODEL="${CHAT_MODEL:-Qwen/Qwen2.5-7B-Instruct}"
EMBED_MODEL="${EMBED_MODEL:-BAAI/bge-m3}"
API_KEY="${VLLM_API_KEY:-change-me-please}"   # protects your public endpoint
LOG_DIR="${LOG_DIR:-/tmp}"

echo "== GPU check =="
(rocm-smi --showproductname || amd-smi list) 2>/dev/null | head -20 || true

echo "== Starting chat model: $CHAT_MODEL on :8000 =="
nohup vllm serve "$CHAT_MODEL" \
  --host 0.0.0.0 --port 8000 \
  --api-key "$API_KEY" \
  --max-model-len 16384 \
  --gpu-memory-utilization 0.45 \
  > "$LOG_DIR/vllm_chat.log" 2>&1 &

# Give the first server time to claim its memory before the second starts.
sleep 60

echo "== Starting embedding model: $EMBED_MODEL on :8001 =="
# Recent vLLM versions detect bge-m3 as an embedding model automatically.
# If your version complains, add:  --task embed   (older)  or  --runner pooling (newer)
nohup vllm serve "$EMBED_MODEL" \
  --host 0.0.0.0 --port 8001 \
  --api-key "$API_KEY" \
  --gpu-memory-utilization 0.15 \
  > "$LOG_DIR/vllm_embed.log" 2>&1 &

echo
echo "Started. Follow the logs with:"
echo "  tail -f $LOG_DIR/vllm_chat.log $LOG_DIR/vllm_embed.log"
echo "When both say 'Application startup complete', run:  bash check_endpoints.sh"
