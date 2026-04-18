#!/bin/bash
# Smoketest for AMD AI Voice Server

API_URL="http://localhost:8000"

echo "--- 🏥 Checking Health ---"
curl -s "$API_URL/health" | grep -q "online" && echo "✅ Server is online" || echo "❌ Server health check failed"

echo "--- 🧠 Testing Text Generation ---"
GEN_TEXT=$(curl -s -X POST "$API_URL/generate" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hej, mår du bra?"}')
if echo "$GEN_TEXT" | grep -q "text"; then
    echo "✅ LLM is responsive"
else
    echo "❌ LLM generation failed"
fi

echo "--- 🔊 Testing Full Process (MP3) ---"
curl -s -X POST "$API_URL/process" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Säg hej på svenska.", "bitrate": "128k"}' \
  --output /tmp/smoke_test.mp3

if [ -f "/tmp/smoke_test.mp3" ] && [ $(stat -c%s "/tmp/smoke_test.mp3") -gt 1000 ]; then
    echo "✅ MP3 generated successfully ($(ls -lh /tmp/smoke_test.mp3 | awk '{print $5}'))"
    rm /tmp/smoke_test.mp3
else
    echo "❌ MP3 generation failed"
fi

echo "--- ✨ Smoketest Complete ---"
