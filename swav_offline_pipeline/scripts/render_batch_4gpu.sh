#!/usr/bin/env bash
# Multi-GPU Batch Rendering Script for 4 GPUs
# Usage: bash render_batch_4gpu.sh
# Distributes 54 shots across 4 GPUs for parallel rendering

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STORYBOARD="${ROOT_DIR}/storyboard.swav2025v2.yaml"
OUTDIR_BASE="${ROOT_DIR}/renders/swav2025"

# GPU assignments (54 shots / 4 GPUs = 13-14 shots each)
GPU0_SHOTS="1-14"    # 14 shots
GPU1_SHOTS="15-28"   # 14 shots
GPU2_SHOTS="29-41"   # 13 shots
GPU3_SHOTS="42-54"   # 13 shots

# Environment setup
if ! command -v conda >/dev/null 2>&1; then
  echo "[ERROR] conda command not found. Please install Miniconda or Anaconda."
  exit 1
fi

set +u
eval "$(conda shell.bash hook)"
set -u
ENV_NAME=$(grep '^name:' "$ROOT_DIR/environment.yml" | head -n1 | cut -d':' -f2 | xargs)

# Activate environment
CURRENT_ENV="${CONDA_DEFAULT_ENV:-}"
if [ "$CURRENT_ENV" != "$ENV_NAME" ]; then
  set +u
  conda activate "$ENV_NAME"
  set -u
fi

# Create output directories
mkdir -p "${OUTDIR_BASE}/gpu0/intermediate"
mkdir -p "${OUTDIR_BASE}/gpu1/intermediate"
mkdir -p "${OUTDIR_BASE}/gpu2/intermediate"
mkdir -p "${OUTDIR_BASE}/gpu3/intermediate"

# Export common environment variables
export LD_LIBRARY_PATH="/usr/local/cuda-12.2/lib64:/usr/local/cuda-12.2/extras/CUPTI/lib64:$HOME/.local/lib/python3.10/site-packages/nvidia/nccl/lib:${LD_LIBRARY_PATH:-}"
export TRANSFORMERS_OFFLINE=1
export HF_HUB_OFFLINE=1
export TF_CPP_MIN_LOG_LEVEL=3
unset TF_ENABLE_ONEDNN_OPTS

echo "=========================================="
echo "SWAVLAMBAN 2025 - MULTI-GPU BATCH RENDER"
echo "=========================================="
echo ""
echo "Total Shots: 54"
echo "GPU Distribution:"
echo "  GPU 0: Shots ${GPU0_SHOTS} (14 shots)"
echo "  GPU 1: Shots ${GPU1_SHOTS} (14 shots)"
echo "  GPU 2: Shots ${GPU2_SHOTS} (13 shots)"
echo "  GPU 3: Shots ${GPU3_SHOTS} (13 shots)"
echo ""
echo "Storyboard: ${STORYBOARD}"
echo "Output Base: ${OUTDIR_BASE}"
echo ""
echo "Starting parallel renders..."
echo "=========================================="
echo ""

# Launch 4 parallel renders (one per GPU)
# NOTE: This requires orchestrate.py to accept --shot-range parameter
# If not implemented, modify orchestrate.py to support this first

# GPU 0 (background)
CUDA_VISIBLE_DEVICES=0 python "${ROOT_DIR}/orchestrate.py" \
  --storyboard "$STORYBOARD" \
  --outdir "${OUTDIR_BASE}/gpu0" \
  --shot-range "$GPU0_SHOTS" \
  --preset "4k" \
  --master "h264" \
  > "${OUTDIR_BASE}/gpu0/render.log" 2>&1 &
PID0=$!
echo "[GPU 0] Started (PID: $PID0) - Shots ${GPU0_SHOTS}"

# GPU 1 (background)
CUDA_VISIBLE_DEVICES=1 python "${ROOT_DIR}/orchestrate.py" \
  --storyboard "$STORYBOARD" \
  --outdir "${OUTDIR_BASE}/gpu1" \
  --shot-range "$GPU1_SHOTS" \
  --preset "4k" \
  --master "h264" \
  > "${OUTDIR_BASE}/gpu1/render.log" 2>&1 &
PID1=$!
echo "[GPU 1] Started (PID: $PID1) - Shots ${GPU1_SHOTS}"

# GPU 2 (background)
CUDA_VISIBLE_DEVICES=2 python "${ROOT_DIR}/orchestrate.py" \
  --storyboard "$STORYBOARD" \
  --outdir "${OUTDIR_BASE}/gpu2" \
  --shot-range "$GPU2_SHOTS" \
  --preset "4k" \
  --master "h264" \
  > "${OUTDIR_BASE}/gpu2/render.log" 2>&1 &
PID2=$!
echo "[GPU 2] Started (PID: $PID2) - Shots ${GPU2_SHOTS}"

# GPU 3 (background)
CUDA_VISIBLE_DEVICES=3 python "${ROOT_DIR}/orchestrate.py" \
  --storyboard "$STORYBOARD" \
  --outdir "${OUTDIR_BASE}/gpu3" \
  --shot-range "$GPU3_SHOTS" \
  --preset "4k" \
  --master "h264" \
  > "${OUTDIR_BASE}/gpu3/render.log" 2>&1 &
PID3=$!
echo "[GPU 3] Started (PID: $PID3) - Shots ${GPU3_SHOTS}"

echo ""
echo "All 4 renders launched in parallel!"
echo ""
echo "Monitor progress with:"
echo "  watch -n 10 'bash ${ROOT_DIR}/../monitor_progress.sh'"
echo ""
echo "Check logs:"
echo "  tail -f ${OUTDIR_BASE}/gpu0/render.log"
echo "  tail -f ${OUTDIR_BASE}/gpu1/render.log"
echo "  tail -f ${OUTDIR_BASE}/gpu2/render.log"
echo "  tail -f ${OUTDIR_BASE}/gpu3/render.log"
echo ""
echo "Wait for all processes to complete..."
echo "PIDs: $PID0 $PID1 $PID2 $PID3"
echo ""

# Wait for all 4 processes to finish
wait $PID0
STATUS0=$?
echo "[GPU 0] Completed with exit code: $STATUS0"

wait $PID1
STATUS1=$?
echo "[GPU 1] Completed with exit code: $STATUS1"

wait $PID2
STATUS2=$?
echo "[GPU 2] Completed with exit code: $STATUS2"

wait $PID3
STATUS3=$?
echo "[GPU 3] Completed with exit code: $STATUS3"

echo ""
echo "=========================================="
echo "BATCH RENDER COMPLETE"
echo "=========================================="
echo ""
echo "Results:"
echo "  GPU 0 (Shots ${GPU0_SHOTS}): $(ls ${OUTDIR_BASE}/gpu0/intermediate/*.mp4 2>/dev/null | wc -l) files"
echo "  GPU 1 (Shots ${GPU1_SHOTS}): $(ls ${OUTDIR_BASE}/gpu1/intermediate/*.mp4 2>/dev/null | wc -l) files"
echo "  GPU 2 (Shots ${GPU2_SHOTS}): $(ls ${OUTDIR_BASE}/gpu2/intermediate/*.mp4 2>/dev/null | wc -l) files"
echo "  GPU 3 (Shots ${GPU3_SHOTS}): $(ls ${OUTDIR_BASE}/gpu3/intermediate/*.mp4 2>/dev/null | wc -l) files"
echo ""
echo "Total rendered: $(find ${OUTDIR_BASE}/gpu*/intermediate/*.mp4 2>/dev/null | wc -l) / 54"
echo ""

# Check for failures
if [ $STATUS0 -ne 0 ] || [ $STATUS1 -ne 0 ] || [ $STATUS2 -ne 0 ] || [ $STATUS3 -ne 0 ]; then
  echo "⚠️  WARNING: Some renders failed. Check logs for details."
  exit 1
else
  echo "✅ All renders completed successfully!"
  echo ""
  echo "Next steps:"
  echo "1. Verify all 54 shots rendered correctly"
  echo "2. Manually stitch clips in your video editor"
  echo "3. Add voiceover and music"
  echo "4. Export final master"
fi
