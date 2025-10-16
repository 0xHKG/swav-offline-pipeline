# Rendering Scripts

## Batch Rendering

### 2-GPU Parallel Rendering (Recommended)
Splits 54 shots across 2 GPUs (odd/even rows):
```bash
bash render_rows_2gpu.sh
```
- GPU 0: r001, r003, r005... r053 (27 shots)
- GPU 1: r002, r004, r006... r054 (27 shots)
- Output: `renders/swav2025_v2/gpu0/` and `gpu1/`

### 4-GPU Parallel Rendering
Distributes shots across 4 GPUs (13-14 shots each):
```bash
bash render_batch_4gpu.sh
```

## Single Shot Rendering

Render one specific shot:
```bash
bash render_single_shot.sh <shot_id> <gpu_id>
```

**Example:**
```bash
bash render_single_shot.sh r001 0  # Render shot r001 on GPU 0
bash render_single_shot.sh r023 1  # Render shot r023 on GPU 1
```

## Live Monitoring

### Dashboard View (Recommended)
Shows GPU stats, progress bars, recent logs, and auto-refreshes:
```bash
bash monitor_live.sh
```

### Raw Log Streaming
Continuous log output from both GPU render processes:
```bash
bash tail_all_logs.sh
```

See [MONITORING.md](../MONITORING.md) for complete monitoring guide.

## Legacy Scripts

- `render.sh` - Original single-GPU sequential rendering (SDXL+SVD, deprecated)
- Used for initial testing, replaced by CogVideoX-based renderers

## Output Structure

```
renders/swav2025_v2/
├── gpu0/
│   ├── intermediate/
│   │   ├── r001.mp4
│   │   ├── r003.mp4
│   │   └── ...
│   └── render.log
├── gpu1/
│   ├── intermediate/
│   │   ├── r002.mp4
│   │   ├── r004.mp4
│   │   └── ...
│   └── render.log
└── combined/
    └── intermediate/
        ├── r001.mp4
        ├── r002.mp4
        └── ... (all 54 shots merged)
```

## Prerequisites

1. CogVideoX-5B model downloaded (18GB)
2. Conda environment `swav_offline` activated
3. CUDA 12.2 installed
4. Both GPUs available

Check model status:
```bash
du -sh ../models/cogvideox-5b
```

Check GPU availability:
```bash
nvidia-smi
```
