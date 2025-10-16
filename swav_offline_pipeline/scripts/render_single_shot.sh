#!/usr/bin/env bash
# Render a single shot from storyboard V2
# Usage: bash render_single_shot.sh <shot_id> <gpu_id>
# Example: bash render_single_shot.sh r001 0

set -euo pipefail

if [ $# -lt 2 ]; then
    echo "Usage: $0 <shot_id> <gpu_id>"
    echo "Example: $0 r001 0"
    exit 1
fi

SHOT_ID=$1
GPU_ID=$2

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STORYBOARD="${ROOT_DIR}/storyboard.swav2025v2.yaml"
OUTDIR="${ROOT_DIR}/renders/swav2025_v2/gpu${GPU_ID}"

# Environment setup
if ! command -v conda >/dev/null 2>&1; then
  echo "[ERROR] conda not found"
  exit 1
fi

set +u
eval "$(conda shell.bash hook)"
set -u
ENV_NAME=$(grep '^name:' "$ROOT_DIR/environment.yml" | head -n1 | cut -d':' -f2 | xargs)

CURRENT_ENV="${CONDA_DEFAULT_ENV:-}"
if [ "$CURRENT_ENV" != "$ENV_NAME" ]; then
  set +u
  conda activate "$ENV_NAME"
  set -u
fi

mkdir -p "$OUTDIR/intermediate"

# Environment variables
export CUDA_VISIBLE_DEVICES=$GPU_ID
export LD_LIBRARY_PATH="/usr/local/cuda-12.2/lib64:/usr/local/cuda-12.2/extras/CUPTI/lib64:$HOME/.local/lib/python3.10/site-packages/nvidia/nccl/lib:${LD_LIBRARY_PATH:-}"
export TRANSFORMERS_OFFLINE=1
export HF_HUB_OFFLINE=1
export TF_CPP_MIN_LOG_LEVEL=3
unset TF_ENABLE_ONEDNN_OPTS

echo "[GPU ${GPU_ID}] Rendering ${SHOT_ID}..."

python "${ROOT_DIR}/render_single_shot.py" \
  --storyboard "$STORYBOARD" \
  --shot-id "$SHOT_ID" \
  --outdir "$OUTDIR" \
  --preset "1080p"

echo "[GPU ${GPU_ID}] ${SHOT_ID} complete!"
