#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STORYBOARD="${ROOT_DIR}/storyboard.swav2025.yaml"
OUTDIR="${ROOT_DIR}/renders/swav2025"

if ! command -v conda >/dev/null 2>&1; then
  echo "[ERROR] conda command not found. Please install Miniconda or Anaconda."
  exit 1
fi

set +u
eval "$(conda shell.bash hook)"
set -u
ENV_NAME=$(grep '^name:' "$ROOT_DIR/environment.yml" | head -n1 | cut -d':' -f2 | xargs)

# Activate environment only if different; relax -u during activation
CURRENT_ENV="${CONDA_DEFAULT_ENV:-}"
if [ "$CURRENT_ENV" != "$ENV_NAME" ]; then
  set +u
  conda activate "$ENV_NAME"
  set -u
fi

mkdir -p "$OUTDIR"

echo "========== RENDER START =========="
python "$ROOT_DIR/orchestrate.py" \
  --storyboard "$STORYBOARD" \
  --outdir "$OUTDIR" \
  --gpus "0,1" \
  --preset "4k" \
  --master "h264" \
  "$@"
echo "========== RENDER COMPLETE =========="
