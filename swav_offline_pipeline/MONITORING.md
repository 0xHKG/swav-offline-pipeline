# Live Monitoring Guide for Swavlamban 2025 Rendering

## Quick Start

### Option 1: Live Dashboard (Recommended)
Shows GPU stats, progress bars, and recent activity in a single refreshing view:

```bash
cd /home/gogi/Desktop/Swavlamban\ 2025/swav_offline_pipeline
bash scripts/monitor_live.sh
```

**Features:**
- Model download progress
- GPU utilization and memory usage (both GPUs)
- Shot completion progress (visual progress bars)
- Recent log entries from both GPUs
- Process status (render + download processes)
- Auto-refreshes every 5 seconds

**Exit:** Press `Ctrl+C`

---

### Option 2: Raw Log Streaming
Shows continuous raw log output from both GPU render processes:

```bash
cd /home/gogi/Desktop/Swavlamban\ 2025/swav_offline_pipeline
bash scripts/tail_all_logs.sh
```

**Features:**
- Real-time log streaming from both GPUs
- Uses `multitail` if available (split-screen view)
- Falls back to standard `tail -f` otherwise

**Exit:** Press `Ctrl+C`

---

## Manual Monitoring Commands

### Check Model Download Status
```bash
# Current download size
du -sh swav_offline_pipeline/models/cogvideox-5b

# Expected: ~18GB when complete
# Current: 5.8GB / 18GB (as of last check)
```

### Check Download Process
```bash
# See if download is still running
ps aux | grep "huggingface-cli download"
```

### GPU Monitoring
```bash
# Real-time GPU stats (updates every 2 seconds)
watch -n 2 nvidia-smi

# Detailed GPU info
nvidia-smi --query-gpu=index,name,memory.used,memory.total,utilization.gpu,temperature.gpu --format=csv
```

### Render Progress
```bash
# Count completed shots per GPU
ls renders/swav2025_v2/gpu0/intermediate/*.mp4 2>/dev/null | wc -l  # Odd rows (max 27)
ls renders/swav2025_v2/gpu1/intermediate/*.mp4 2>/dev/null | wc -l  # Even rows (max 27)

# Total progress
find renders/swav2025_v2/gpu*/intermediate/*.mp4 2>/dev/null | wc -l  # Total (max 54)
```

### Check Render Logs
```bash
# GPU 0 (odd shots: r001, r003, r005...)
tail -f renders/swav2025_v2/gpu0/render.log

# GPU 1 (even shots: r002, r004, r006...)
tail -f renders/swav2025_v2/gpu1/render.log

# Last 50 lines from both
tail -n 50 renders/swav2025_v2/gpu0/render.log
tail -n 50 renders/swav2025_v2/gpu1/render.log
```

### Process Status
```bash
# Check if renders are running
ps aux | grep "render_"

# Check render PIDs from launch script
# (PIDs are printed when render_rows_2gpu.sh starts)
```

---

## Understanding the Output

### Dashboard View (monitor_live.sh)

```
═══════════════════════════════════════════════════════════════
         SWAVLAMBAN 2025 - LIVE RENDERING MONITOR
═══════════════════════════════════════════════════════════════

📥 CogVideoX-5B Download: 5.8G / ~18GB (IN PROGRESS)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GPU STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GPU 0 [NVIDIA RTX A6000]: 85% util | 18432MB / 49140MB (37%) | 68°C
GPU 1 [NVIDIA RTX A6000]: 82% util | 17891MB / 49140MB (36%) | 67°C

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RENDER PROGRESS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GPU 0 (Odd Rows):  5 / 27 shots ██████████
GPU 1 (Even Rows): 6 / 27 shots ████████████
Total Progress:    11 / 54 shots (20%)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROCESS STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ 4 render process(es) running
  PID 153439: /bin/bash render_rows_2gpu.sh
  PID 153763: python render_cogvideox.py --shot-id r007
⏳ Model download in progress

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RECENT ACTIVITY (Last 10 lines per GPU)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[GPU 0]
  [GPU 0] Rendering r005...
  Loading CogVideoX pipeline...
  Prompt: Wide-angle tactical display showing real-time fleet...
  Exporting to renders/swav2025_v2/gpu0/intermediate/r005.mp4...
  ✓ r005 complete!

[GPU 1]
  [GPU 1] Rendering r006...
  Loading CogVideoX pipeline...
  Prompt: Close-up: Ship's combat information center (CIC)...
  Exporting to renders/swav2025_v2/gpu1/intermediate/r006.mp4...
  ✓ r006 complete!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Last updated: 2025-10-17 00:25:34
Refreshing in 5 seconds... (Ctrl+C to exit)
```

### Log Indicators

- **Model Loading:** `Loading CogVideoX pipeline...` (happens once per shot)
- **Generation Start:** `Prompt: ...` (shows the shot's prompt)
- **Export Phase:** `Exporting to .../*.mp4` (frames → video file)
- **Completion:** `✓ [shot_id] complete!` (shot finished successfully)
- **Error:** `✗ [shot_id] FAILED` (shot encountered an error)

---

## Expected Timeline

### Phase 1: Model Download (Current)
- **Status:** 5.8GB / 18GB downloaded
- **Time Remaining:** ~10-20 minutes (depends on network speed)
- **Action:** Wait for download to complete before starting renders

### Phase 2: Batch Rendering (After Download)
- **Launch Command:**
  ```bash
  cd /home/gogi/Desktop/Swavlamban\ 2025/swav_offline_pipeline
  bash scripts/render_rows_2gpu.sh
  ```
- **Total Shots:** 54 (27 per GPU)
- **Time per Shot:** ~2-3 minutes
- **Total Duration:** ~68 minutes (both GPUs in parallel)

### Phase 3: Review & Stitch
- **Location:** `renders/swav2025_v2/combined/intermediate/`
- **Files:** `r001.mp4` through `r054.mp4`
- **Next Steps:** Manual video editing to stitch shots in order

---

## Troubleshooting

### "No render logs found yet"
**Cause:** Rendering hasn't started yet
**Fix:** Launch render with `bash scripts/render_rows_2gpu.sh`

### "Model directory not found or empty"
**Cause:** Download not started or directory deleted
**Fix:** Re-run download command from previous session

### "GPU utilization 0%"
**Cause:** Render process stuck or not started
**Fix:**
1. Check process status: `ps aux | grep render`
2. Check logs for errors: `tail -50 renders/swav2025_v2/gpu*/render.log`
3. Restart render if needed

### "CUDA out of memory"
**Cause:** VRAM exhausted (unlikely with CogVideoX + memory optimizations)
**Fix:**
1. Kill other GPU processes: `nvidia-smi` → note PID → `kill <PID>`
2. Reduce resolution in render_cogvideox.py (currently 720x480)

---

## File Locations

### Scripts
- **Main Render:** `scripts/render_rows_2gpu.sh`
- **Single Shot:** `scripts/render_single_shot.sh <shot_id> <gpu_id>`
- **Live Dashboard:** `scripts/monitor_live.sh`
- **Log Viewer:** `scripts/tail_all_logs.sh`

### Models
- **CogVideoX-5B:** `models/cogvideox-5b/` (18GB when complete)
- **XTTS v2:** `models/xtts-v2/` (2GB)
- **MusicGen:** `models/musicgen-small/` (5.5GB)

### Output
- **GPU 0 Shots:** `renders/swav2025_v2/gpu0/intermediate/` (odd: r001, r003...)
- **GPU 1 Shots:** `renders/swav2025_v2/gpu1/intermediate/` (even: r002, r004...)
- **Combined:** `renders/swav2025_v2/combined/intermediate/` (all 54 shots)
- **Logs:** `renders/swav2025_v2/gpu0/render.log` and `gpu1/render.log`

### Configuration
- **Storyboard:** `storyboard.swav2025v2.yaml` (54 shot definitions)
- **Environment:** `environment.yml` (conda dependencies)

---

## Tips

1. **Leave monitor running in tmux/screen** for long renders:
   ```bash
   tmux new -s monitor
   bash scripts/monitor_live.sh
   # Detach: Ctrl+B then D
   # Reattach later: tmux attach -t monitor
   ```

2. **Check progress remotely via SSH:**
   ```bash
   ssh user@machine "cd /path/to/project && find renders/swav2025_v2/gpu*/intermediate -name '*.mp4' | wc -l"
   ```

3. **Estimate remaining time:**
   ```bash
   # Example: If 11/54 shots done in 27 minutes
   # Remaining: (54 - 11) / 2 GPUs × 2.5 min/shot ≈ 54 minutes
   ```

4. **Review specific shot without downloading:**
   ```bash
   # Check file size (should be 10-30MB per 6-second shot)
   ls -lh renders/swav2025_v2/combined/intermediate/r001.mp4

   # Play with mpv/vlc if on local machine
   mpv renders/swav2025_v2/combined/intermediate/r001.mp4
   ```
