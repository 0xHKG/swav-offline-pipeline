#!/usr/bin/env bash
# Live Monitoring Dashboard for Swavlamban 2025 Batch Rendering
# Shows real-time progress across all processes

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTDIR_BASE="${ROOT_DIR}/renders/swav2025_v2"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Clear screen and show header
clear
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}         SWAVLAMBAN 2025 - LIVE RENDERING MONITOR              ${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Function to check model download status
check_model_download() {
    local MODEL_DIR="${ROOT_DIR}/models/cogvideox-5b"
    local MODEL_SIZE_GB=$(du -sh "$MODEL_DIR" 2>/dev/null | cut -f1 || echo "0")

    if pgrep -f "huggingface-cli download" >/dev/null; then
        echo -e "${YELLOW}📥 CogVideoX-5B Download: ${MODEL_SIZE_GB} / ~18GB (IN PROGRESS)${NC}"
    else
        if [ -d "$MODEL_DIR" ]; then
            echo -e "${GREEN}✓ CogVideoX-5B Ready: ${MODEL_SIZE_GB}${NC}"
        else
            echo -e "${RED}✗ CogVideoX-5B Not Downloaded${NC}"
        fi
    fi
}

# Function to show GPU status
show_gpu_status() {
    echo -e "\n${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${MAGENTA}GPU STATUS${NC}"
    echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    nvidia-smi --query-gpu=index,name,memory.used,memory.total,utilization.gpu,temperature.gpu --format=csv,noheader,nounits | \
    while IFS=, read -r idx name mem_used mem_total util temp; do
        mem_used=$(echo "$mem_used" | xargs)
        mem_total=$(echo "$mem_total" | xargs)
        util=$(echo "$util" | xargs)
        temp=$(echo "$temp" | xargs)

        mem_pct=$((mem_used * 100 / mem_total))

        if [ "$util" -gt 80 ]; then
            util_color="${GREEN}"
        elif [ "$util" -gt 30 ]; then
            util_color="${YELLOW}"
        else
            util_color="${NC}"
        fi

        echo -e "${BLUE}GPU ${idx}${NC} [${name}]: ${util_color}${util}% util${NC} | ${mem_used}MB / ${mem_total}MB (${mem_pct}%) | ${temp}°C"
    done
}

# Function to show render progress
show_render_progress() {
    echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}RENDER PROGRESS${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    # Check if render directories exist
    local GPU0_DIR="${OUTDIR_BASE}/gpu0/intermediate"
    local GPU1_DIR="${OUTDIR_BASE}/gpu1/intermediate"
    local COMBINED_DIR="${OUTDIR_BASE}/combined/intermediate"

    if [ -d "$GPU0_DIR" ]; then
        local gpu0_count=$(ls "$GPU0_DIR"/*.mp4 2>/dev/null | wc -l)
        echo -e "${BLUE}GPU 0 (Odd Rows):${NC}  ${gpu0_count} / 27 shots ${GREEN}$(printf '█%.0s' $(seq 1 $((gpu0_count * 2))))${NC}"
    else
        echo -e "${YELLOW}GPU 0: Not started${NC}"
    fi

    if [ -d "$GPU1_DIR" ]; then
        local gpu1_count=$(ls "$GPU1_DIR"/*.mp4 2>/dev/null | wc -l)
        echo -e "${BLUE}GPU 1 (Even Rows):${NC} ${gpu1_count} / 27 shots ${GREEN}$(printf '█%.0s' $(seq 1 $((gpu1_count * 2))))${NC}"
    else
        echo -e "${YELLOW}GPU 1: Not started${NC}"
    fi

    if [ -d "$GPU0_DIR" ] || [ -d "$GPU1_DIR" ]; then
        local total=$((gpu0_count + gpu1_count))
        local pct=$((total * 100 / 54))
        echo -e "${CYAN}Total Progress:${NC}    ${total} / 54 shots (${pct}%)"
    fi
}

# Function to show recent log entries
show_recent_logs() {
    echo -e "\n${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}RECENT ACTIVITY (Last 10 lines per GPU)${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    local GPU0_LOG="${OUTDIR_BASE}/gpu0/render.log"
    local GPU1_LOG="${OUTDIR_BASE}/gpu1/render.log"

    if [ -f "$GPU0_LOG" ]; then
        echo -e "\n${BLUE}[GPU 0]${NC}"
        tail -n 10 "$GPU0_LOG" | sed 's/^/  /'
    fi

    if [ -f "$GPU1_LOG" ]; then
        echo -e "\n${BLUE}[GPU 1]${NC}"
        tail -n 10 "$GPU1_LOG" | sed 's/^/  /'
    fi
}

# Function to show process status
show_process_status() {
    echo -e "\n${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}PROCESS STATUS${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    # Check for render processes
    local render_procs=$(pgrep -f "render_single_shot.py\|render_cogvideox.py\|render_rows_2gpu.sh" | wc -l)
    if [ "$render_procs" -gt 0 ]; then
        echo -e "${GREEN}✓ ${render_procs} render process(es) running${NC}"
        ps aux | grep -E "(render_single_shot|render_cogvideox|render_rows_2gpu)" | grep -v grep | \
        awk '{printf "  PID %s: %s %s %s %s\n", $2, $11, $12, $13, $14}'
    else
        echo -e "${YELLOW}⊗ No render processes running${NC}"
    fi

    # Check for download process
    if pgrep -f "huggingface-cli download" >/dev/null; then
        echo -e "${YELLOW}⏳ Model download in progress${NC}"
    fi
}

# Main monitoring loop
echo -e "${CYAN}Starting live monitor... (Press Ctrl+C to exit)${NC}"
echo ""

check_model_download

while true; do
    # Move cursor to top (preserve header)
    tput cup 6 0

    check_model_download
    show_gpu_status
    show_render_progress
    show_process_status
    show_recent_logs

    echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}Last updated: $(date '+%Y-%m-%d %H:%M:%S')${NC}"
    echo -e "${CYAN}Refreshing in 5 seconds... (Ctrl+C to exit)${NC}"

    sleep 5
done
