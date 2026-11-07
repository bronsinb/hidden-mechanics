#!/usr/bin/env bash
# One-time setup in a fresh cloud workspace: Python packages + the narration voice model (~350 MB).
set -e
pip install --break-system-packages -q kokoro-onnx soundfile pycairo pillow numpy 2>&1 | grep -v -i warning || true
TTS="${HM_TTS:-/home/claude/tts}"
mkdir -p "$TTS"
[ -s "$TTS/kokoro-v11.onnx" ] || curl -sSL -o "$TTS/kokoro-v11.onnx" https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.1/kokoro-v1.0.onnx
[ -s "$TTS/voices-v1.0.bin" ] || curl -sSL -o "$TTS/voices-v1.0.bin" https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
python3 -c "import cairo, kokoro_onnx, soundfile; print('setup ok')"
fc-list | grep -q "Inter" && echo "fonts ok" || echo "WARNING: Inter font missing - install fonts-inter"
