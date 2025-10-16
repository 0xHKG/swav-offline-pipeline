#!/usr/bin/env bash
# Row-wise Batch Rendering for Storyboard V2 with 2 GPUs
# Splits 54 shots between GPU 0 (odd rows) and GPU 1 (even rows)
# Usage: bash render_rows_2gpu.sh

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STORYBOARD="${ROOT_DIR}/storyboard.swav2025v2.yaml"
OUTDIR_BASE="${ROOT_DIR}/renders/swav2025_v2"

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
mkdir -p "${OUTDIR_BASE}/combined/intermediate"

# Export common environment variables
export LD_LIBRARY_PATH="/usr/local/cuda-12.2/lib64:/usr/local/cuda-12.2/extras/CUPTI/lib64:$HOME/.local/lib/python3.10/site-packages/nvidia/nccl/lib:${LD_LIBRARY_PATH:-}"
export TRANSFORMERS_OFFLINE=1
export HF_HUB_OFFLINE=1
export TF_CPP_MIN_LOG_LEVEL=3
unset TF_ENABLE_ONEDNN_OPTS

echo "=============================================="
echo "SWAVLAMBAN 2025 - ROW-WISE 2-GPU BATCH RENDER"
echo "=============================================="
echo ""
echo "Total Shots: 54 (r001 to r054)"
echo "GPU 0: Odd rows  (r001, r003, r005... r053) = 27 shots"
echo "GPU 1: Even rows (r002, r004, r006... r054) = 27 shots"
echo ""
echo "Storyboard: ${STORYBOARD}"
echo "Output: ${OUTDIR_BASE}"
echo ""
echo "Starting parallel renders..."
echo "=============================================="
echo ""

# Function to render specific shots
render_shots() {
    local GPU_ID=$1
    local START_NUM=$2
    local OUTDIR=$3
    local LOG_FILE="${OUTDIR}/render.log"

    echo "[GPU ${GPU_ID}] Starting render (shots ${START_NUM}, +2 increment)" >> "$LOG_FILE"

    # Render shots r001, r003, r005... (odd) or r002, r004, r006... (even)
    for i in $(seq $START_NUM 2 54); do
        SHOT_ID=$(printf "r%03d" $i)
        echo "[GPU ${GPU_ID}] Rendering ${SHOT_ID}..." | tee -a "$LOG_FILE"

        CUDA_VISIBLE_DEVICES=${GPU_ID} python "${ROOT_DIR}/render_single_shot.py" \
            --storyboard "$STORYBOARD" \
            --shot-id "$SHOT_ID" \
            --outdir "$OUTDIR" \
            --preset "1080p" \
            >> "$LOG_FILE" 2>&1

        if [ $? -eq 0 ]; then
            echo "[GPU ${GPU_ID}] ✓ ${SHOT_ID} complete" | tee -a "$LOG_FILE"
        else
            echo "[GPU ${GPU_ID}] ✗ ${SHOT_ID} FAILED" | tee -a "$LOG_FILE"
        fi
    done

    echo "[GPU ${GPU_ID}] All shots complete" | tee -a "$LOG_FILE"
}

# Launch GPU 0 (odd shots: 1, 3, 5, 7... 53)
(render_shots 0 1 "${OUTDIR_BASE}/gpu0") &
PID0=$!
echo "[GPU 0] Launched (PID: $PID0) - Odd shots (r001, r003, r005...)"

# Launch GPU 1 (even shots: 2, 4, 6, 8... 54)
(render_shots 1 2 "${OUTDIR_BASE}/gpu1") &
PID1=$!
echo "[GPU 1] Launched (PID: $PID1) - Even shots (r002, r004, r006...)"

echo ""
echo "Both renders running in parallel!"
echo ""
echo "Monitor progress:"
echo "  GPU 0: tail -f ${OUTDIR_BASE}/gpu0/render.log"
echo "  GPU 1: tail -f ${OUTDIR_BASE}/gpu1/render.log"
echo ""
echo "Watch files:"
echo "  watch -n 10 'ls ${OUTDIR_BASE}/gpu*/intermediate/*.mp4 | wc -l'"
echo ""

# Wait for completion
echo "Waiting for GPU 0..."
wait $PID0
STATUS0=$?
echo "[GPU 0] Exit code: $STATUS0"

echo "Waiting for GPU 1..."
wait $PID1
STATUS1=$?
echo "[GPU 1] Exit code: $STATUS1"

echo ""
echo "=============================================="
echo "BATCH RENDER COMPLETE"
echo "=============================================="
echo ""

# Count results
GPU0_COUNT=$(ls "${OUTDIR_BASE}/gpu0/intermediate/"*.mp4 2>/dev/null | wc -l)
GPU1_COUNT=$(ls "${OUTDIR_BASE}/gpu1/intermediate/"*.mp4 2>/dev/null | wc -l)
TOTAL_COUNT=$((GPU0_COUNT + GPU1_COUNT))

echo "Results:"
echo "  GPU 0 (odd rows):  ${GPU0_COUNT} / 27 shots"
echo "  GPU 1 (even rows): ${GPU1_COUNT} / 27 shots"
echo "  Total:             ${TOTAL_COUNT} / 54 shots"
echo ""

# Merge shots into combined directory
echo "Merging shots into combined directory..."
cp "${OUTDIR_BASE}/gpu0/intermediate/"*.mp4 "${OUTDIR_BASE}/combined/intermediate/" 2>/dev/null || true
cp "${OUTDIR_BASE}/gpu1/intermediate/"*.mp4 "${OUTDIR_BASE}/combined/intermediate/" 2>/dev/null || true
echo "Combined: $(ls ${OUTDIR_BASE}/combined/intermediate/*.mp4 2>/dev/null | wc -l) shots"
echo ""

if [ $STATUS0 -ne 0 ] || [ $STATUS1 -ne 0 ]; then
  echo "⚠️  WARNING: Some renders failed. Check logs."
  exit 1
else
  echo "✅ All renders completed successfully!"
  echo ""
  echo "Next steps:"
  echo "1. Review shots in: ${OUTDIR_BASE}/combined/intermediate/"
  echo "2. Manually stitch clips in video editor (preserves r001-r054 order)"
  echo "3. Add voiceover narration using XTTS v2"
  echo "4. Export final master"
fi
