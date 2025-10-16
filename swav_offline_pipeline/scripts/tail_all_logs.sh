#!/usr/bin/env bash
# Tail all render logs simultaneously using multitail
# Shows raw log output from both GPUs in split-screen view

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTDIR_BASE="${ROOT_DIR}/renders/swav2025_v2"

GPU0_LOG="${OUTDIR_BASE}/gpu0/render.log"
GPU1_LOG="${OUTDIR_BASE}/gpu1/render.log"

# Check if logs exist
if [ ! -f "$GPU0_LOG" ] && [ ! -f "$GPU1_LOG" ]; then
    echo "No render logs found yet."
    echo ""
    echo "Expected locations:"
    echo "  - ${GPU0_LOG}"
    echo "  - ${GPU1_LOG}"
    echo ""
    echo "Start rendering first with: bash scripts/render_rows_2gpu.sh"
    exit 1
fi

# Try to use multitail if available, otherwise fall back to tail
if command -v multitail >/dev/null 2>&1; then
    echo "Using multitail for split-screen view..."
    if [ -f "$GPU0_LOG" ] && [ -f "$GPU1_LOG" ]; then
        multitail -s 2 -sn 1,GPU0 "$GPU0_LOG" -sn 2,GPU1 "$GPU1_LOG"
    elif [ -f "$GPU0_LOG" ]; then
        multitail "$GPU0_LOG"
    else
        multitail "$GPU1_LOG"
    fi
else
    # Fallback: use tail with color coding
    echo "====================================================================="
    echo "LIVE LOG VIEWER (Ctrl+C to exit)"
    echo "====================================================================="
    echo ""
    echo "GPU 0 Log: $GPU0_LOG"
    echo "GPU 1 Log: $GPU1_LOG"
    echo ""
    echo "Streaming logs..."
    echo "====================================================================="
    echo ""

    # Tail both files simultaneously with labels
    if [ -f "$GPU0_LOG" ] && [ -f "$GPU1_LOG" ]; then
        tail -f "$GPU0_LOG" "$GPU1_LOG"
    elif [ -f "$GPU0_LOG" ]; then
        tail -f "$GPU0_LOG"
    else
        tail -f "$GPU1_LOG"
    fi
fi
