# Swavlamban 2025 - Quick Start Guide

## Current Status

**CogVideoX-5B Download:** 15GB / 18GB (83% complete)

Once download completes, follow these steps to begin rendering.

---

## Step 1: Verify Model Download Complete

```bash
cd /home/gogi/Desktop/Swavlamban\ 2025/swav_offline_pipeline

# Should show ~18GB
du -sh models/cogvideox-5b

# Check if download process finished
ps aux | grep huggingface-cli
```

If download still running, wait for completion before proceeding.

---

## Step 2: Activate Environment

```bash
# Activate conda environment
conda activate swav_offline

# Verify CUDA available
nvidia-smi
```

Expected: Both RTX A6000 GPUs visible with ~49GB VRAM each.

---

## Step 3: Start 2-GPU Batch Rendering

```bash
# Launch parallel rendering across both GPUs
bash scripts/render_rows_2gpu.sh
```

This will:
- Render shots r001, r003, r005... r053 on GPU 0 (27 shots)
- Render shots r002, r004, r006... r054 on GPU 1 (27 shots)
- Save outputs to `renders/swav2025_v2/gpu0/` and `gpu1/`
- Log progress to `renders/swav2025_v2/gpu0/render.log` and `gpu1/render.log`

Expected total time: **~68 minutes** (2-3 min per shot × 27 shots per GPU)

---

## Step 4: Monitor Progress

### Option A: Live Dashboard (Recommended)

In a **new terminal window**:

```bash
cd /home/gogi/Desktop/Swavlamban\ 2025/swav_offline_pipeline
bash scripts/monitor_live.sh
```

Shows:
- GPU utilization and VRAM usage
- Progress bars (shots completed / 27 per GPU)
- Recent log entries from both GPUs
- Process status
- Auto-refreshes every 5 seconds

Press `Ctrl+C` to exit.

### Option B: Raw Log Streaming

```bash
cd /home/gogi/Desktop/Swavlamban\ 2025/swav_offline_pipeline
bash scripts/tail_all_logs.sh
```

Shows continuous log output from both render processes.

### Option C: Manual Checks

```bash
# Count completed shots
ls renders/swav2025_v2/gpu0/intermediate/*.mp4 | wc -l  # GPU 0 (max 27)
ls renders/swav2025_v2/gpu1/intermediate/*.mp4 | wc -l  # GPU 1 (max 27)

# Watch GPU usage
watch -n 2 nvidia-smi

# View recent logs
tail -f renders/swav2025_v2/gpu0/render.log  # GPU 0
tail -f renders/swav2025_v2/gpu1/render.log  # GPU 1
```

---

## Step 5: Review Rendered Shots

Once rendering completes:

```bash
# All shots merged into combined directory
ls renders/swav2025_v2/combined/intermediate/

# Should contain r001.mp4 through r054.mp4
```

Each shot:
- Resolution: 720×480 (CogVideoX native)
- Duration: 6 seconds (49 frames @ 8fps, exported at 30fps)
- Format: MP4 (H.264)
- Size: ~10-30MB per shot

### Preview a Shot

```bash
# Using mpv (if installed)
mpv renders/swav2025_v2/combined/intermediate/r001.mp4

# Or copy to another machine to review
```

---

## Step 6: Manual Stitching & Post-Production

The 54 shots are designed to be manually stitched in a video editor for maximum control:

1. **Import shots** into your video editor (DaVinci Resolve, Premiere Pro, Final Cut, etc.)
2. **Arrange in order** r001 → r054 (already named sequentially)
3. **Add transitions** between shots (fades, cuts, etc.)
4. **Add voiceover narration** using XTTS v2 (if not already embedded)
5. **Add background music** (optional - MusicGen or custom)
6. **Color grading** for professional polish
7. **Export final master** (H.264 1080p or 4K upscaled)

---

## Troubleshooting

### "Permission denied" on scripts
```bash
chmod +x scripts/*.sh
```

### "Conda environment not found"
```bash
# Check environment name
conda env list

# Should show: swav_offline

# If missing, recreate:
conda env create -f environment.yml
```

### "CUDA out of memory"
This shouldn't happen with CogVideoX + memory optimizations, but if it does:

1. Check other GPU processes: `nvidia-smi`
2. Kill competing processes if found
3. Restart render

### Render process stuck
```bash
# Check logs for errors
tail -50 renders/swav2025_v2/gpu0/render.log
tail -50 renders/swav2025_v2/gpu1/render.log

# If truly stuck, kill and restart:
pkill -f render_rows_2gpu
bash scripts/render_rows_2gpu.sh
```

### Poor video quality
CogVideoX-5B should produce much better quality than the previous SDXL+SVD approach. If quality is still unsatisfactory:

1. Review sample shots (r001, r002, etc.)
2. Check if prompts need refinement in [storyboard.swav2025v2.yaml](swav_offline_pipeline/storyboard.swav2025v2.yaml)
3. Consider upscaling to 1080p using video enhancer (Topaz Video AI, etc.)

---

## Advanced: Single Shot Re-rendering

If a specific shot needs to be re-rendered:

```bash
# Syntax: bash scripts/render_single_shot.sh <shot_id> <gpu_id>

# Example: Re-render shot r023 on GPU 0
bash scripts/render_single_shot.sh r023 0

# Output: renders/swav2025_v2/gpu0/intermediate/r023.mp4
```

---

## Next Steps After Rendering

1. **Quality Review:** Watch all 54 shots, note any that need re-rendering
2. **Backup Renders:** Copy `renders/swav2025_v2/combined/` to safe location
3. **Begin Editing:** Import into video editor and start post-production
4. **Generate Narration:** Use XTTS v2 for voiceover (if needed)
5. **Final Export:** Create exhibition-ready master file

---

## File Locations Reference

- **Scripts:** [swav_offline_pipeline/scripts/](swav_offline_pipeline/scripts/)
- **Models:** [swav_offline_pipeline/models/](swav_offline_pipeline/models/)
- **Storyboard:** [swav_offline_pipeline/storyboard.swav2025v2.yaml](swav_offline_pipeline/storyboard.swav2025v2.yaml)
- **Renders:** [swav_offline_pipeline/renders/swav2025_v2/](swav_offline_pipeline/renders/swav2025_v2/)
- **Logs:** [swav_offline_pipeline/renders/swav2025_v2/gpu0/render.log](swav_offline_pipeline/renders/swav2025_v2/gpu0/render.log)
- **Documentation:** [CLAUDE.md](CLAUDE.md) (full session history) | [MONITORING.md](swav_offline_pipeline/MONITORING.md) (monitoring guide)

---

## System Specs (Current Machine)

- **CPU:** AMD Ryzen Threadripper PRO 7985WX (128 cores)
- **RAM:** 256GB DDR5
- **GPUs:** 2× NVIDIA RTX A6000 (49GB VRAM each)
- **CUDA:** 12.2
- **OS:** Ubuntu 22.04 LTS

---

## Support

For issues or questions, refer to:
- [CLAUDE.md](CLAUDE.md) - Complete project documentation and session history
- [MONITORING.md](swav_offline_pipeline/MONITORING.md) - Detailed monitoring guide
- [scripts/README.md](swav_offline_pipeline/scripts/README.md) - Script reference

---

**Ready to render!** Once the CogVideoX-5B download completes, run:

```bash
cd /home/gogi/Desktop/Swavlamban\ 2025/swav_offline_pipeline
bash scripts/render_rows_2gpu.sh
```

Then monitor with:

```bash
bash scripts/monitor_live.sh
```
