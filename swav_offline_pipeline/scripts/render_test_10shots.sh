#!/usr/bin/env bash
# Test render: First 10 shots across 2 GPUs (5 odd, 5 even)
# GPU 0: r001, r003, r005, r007, r009
# GPU 1: r002, r004, r006, r008, r010

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STORYBOARD="${ROOT_DIR}/storyboard.swav2025v2.yaml"
OUTDIR_BASE="${ROOT_DIR}/renders/swav2025_v2_test"

# Create output directories
mkdir -p "${OUTDIR_BASE}/gpu0/intermediate"
mkdir -p "${OUTDIR_BASE}/gpu1/intermediate"
mkdir -p "${OUTDIR_BASE}/combined/intermediate"

echo "=========================================="
echo "TEST RENDER: First 10 Shots (CogVideoX-5B)"
echo "=========================================="
echo ""
echo "GPU 0: r001, r003, r005, r007, r009 (5 shots)"
echo "GPU 1: r002, r004, r006, r008, r010 (5 shots)"
echo ""
echo "Output: ${OUTDIR_BASE}"
echo ""

# Activate conda environment
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate swav_offline

# Function to render shots on a specific GPU
render_shots() {
    local GPU_ID=$1
    local OUTDIR=$2
    shift 2
    local SHOTS=("$@")

    for SHOT_ID in "${SHOTS[@]}"; do
        echo "[GPU ${GPU_ID}] Rendering ${SHOT_ID}..."

        CUDA_VISIBLE_DEVICES=${GPU_ID} conda run -n swav_offline python "${ROOT_DIR}/render_cogvideox.py" \
            --storyboard "$STORYBOARD" \
            --shot-id "$SHOT_ID" \
            --outdir "$OUTDIR" \
            --preset "720p" \
            2>&1 | tee -a "${OUTDIR}/render.log"

        # Copy to combined directory
        if [ -f "${OUTDIR}/intermediate/${SHOT_ID}.mp4" ]; then
            cp "${OUTDIR}/intermediate/${SHOT_ID}.mp4" "${OUTDIR_BASE}/combined/intermediate/"
            echo "[GPU ${GPU_ID}] ✓ ${SHOT_ID} complete!"
        else
            echo "[GPU ${GPU_ID}] ✗ ${SHOT_ID} FAILED!"
        fi
    done
}

# GPU 0: First 5 odd shots
GPU0_SHOTS=(r001 r003 r005 r007 r009)

# GPU 1: First 5 even shots
GPU1_SHOTS=(r002 r004 r006 r008 r010)

echo "Starting parallel rendering..."
echo ""

# Launch both GPUs in parallel
render_shots 0 "${OUTDIR_BASE}/gpu0" "${GPU0_SHOTS[@]}" &
PID_GPU0=$!

render_shots 1 "${OUTDIR_BASE}/gpu1" "${GPU1_SHOTS[@]}" &
PID_GPU1=$!

echo "GPU 0 PID: ${PID_GPU0}"
echo "GPU 1 PID: ${PID_GPU1}"
echo ""
echo "Monitor progress with:"
echo "  bash scripts/monitor_live.sh"
echo ""
echo "View logs:"
echo "  tail -f ${OUTDIR_BASE}/gpu0/render.log"
echo "  tail -f ${OUTDIR_BASE}/gpu1/render.log"
echo ""

# Wait for both to complete
wait $PID_GPU0
wait $PID_GPU1

echo ""
echo "=========================================="
echo "TEST RENDER COMPLETE!"
echo "=========================================="
echo ""
echo "Review outputs at:"
echo "  ${OUTDIR_BASE}/combined/intermediate/"
echo ""
echo "Files: r001.mp4 through r010.mp4 (10 test shots)"
echo ""

# List completed shots
echo "Completed shots:"
ls -lh "${OUTDIR_BASE}/combined/intermediate/"*.mp4 2>/dev/null || echo "No shots completed"
