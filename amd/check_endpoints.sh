#!/usr/bin/env bash
# Quick health check for both vLLM servers. Run on the droplet, or from
# your laptop with HOST set to the droplet's public IP.
set -uo pipefail

HOST="${HOST:-localhost}"
API_KEY="${VLLM_API_KEY:-change-me-please}"

echo "== Models on :8000 (chat) =="
curl -s "http://$HOST:8000/v1/models" -H "Authorization: Bearer $API_KEY"; echo

echo "== Models on :8001 (embeddings) =="
curl -s "http://$HOST:8001/v1/models" -H "Authorization: Bearer $API_KEY"; echo

echo "== Chat test =="
curl -s "http://$HOST:8000/v1/chat/completions" \
  -H "Content-Type: application/json" -H "Authorization: Bearer $API_KEY" \
  -d '{"model":"Qwen/Qwen2.5-7B-Instruct","messages":[{"role":"user","content":"Say hello from an AMD GPU in one sentence."}],"max_tokens":40}'
echo

echo "== Embedding test (prints vector length) =="
curl -s "http://$HOST:8001/v1/embeddings" \
  -H "Content-Type: application/json" -H "Authorization: Bearer $API_KEY" \
  -d '{"model":"BAAI/bge-m3","input":"hydraulic pressure too low"}' \
  | python3 -c 'import sys,json; d=json.load(sys.stdin); print(len(d["data"][0]["embedding"]))'
