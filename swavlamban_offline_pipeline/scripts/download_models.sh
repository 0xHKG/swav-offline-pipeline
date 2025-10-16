#!/usr/bin/env bash
set -euo pipefail
pip install --upgrade huggingface_hub
mkdir -p models
huggingface-cli download stabilityai/stable-diffusion-xl-base-1.0 --local-dir models/sdxl-base --exclude "*.bin"
huggingface-cli download stabilityai/stable-video-diffusion-img2vid-xt --local-dir models/svd-img2vid --exclude "*.bin"
huggingface-cli download coqui/XTTS-v2 --local-dir models/xtts-v2
huggingface-cli download facebook/musicgen-small --local-dir models/musicgen-small
mkdir -p models/rife models/realesrgan
echo "Place RIFE/Real-ESRGAN weights under models/rife and models/realesrgan if used."
