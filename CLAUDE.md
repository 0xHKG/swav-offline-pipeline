# SWAVLAMBAN 2025 - AI Video Generation Pipeline

**Project:** Indian Navy Innovation Exhibition Film
**Venue:** Manekshaw Centre, New Delhi
**Dates:** 25-26 November 2025
**Last Updated:** 2025-10-16 23:47 IST
**Session Status:** IN PROGRESS - Continue on 4-GPU machine tomorrow

---

## 📋 PROJECT OVERVIEW

Automated offline video production pipeline for generating a 54-shot exhibition film showcasing Indian Navy innovations across 15 capability categories using AI-generated visuals, text-to-speech narration, and professional post-processing.

**Tagline:** "STRENGTH & POWER THROUGH INNOVATION AND INDIGENISATION" (नवाचार एवं स्वदेशीकरण से सशक्तिकरण)

---

## 🎯 CURRENT STATUS SUMMARY

### ✅ Completed Today (2025-10-16)
1. **Environment Setup** - Python 3.10 + CUDA 12.1 conda environment created
2. **AI Models Downloaded** (110GB total):
   - Stable Diffusion XL Base (72GB)
   - Stable Video Diffusion img2vid (31GB)
   - XTTS v2 Text-to-Speech (2GB)
   - MusicGen Small (5.5GB)
3. **Dependencies Installed** - All 26 required packages working
4. **Test Render** - Shot 001 completed successfully (39MB, 4K @ 30fps, 7 seconds)

### ⚠️ Issues Encountered
1. **CUDA OOM Error** - 4K video generation at shot 2 exhausted 49GB VRAM on single GPU
2. **Visual Quality Concern** - AI-generated backgrounds appear pixelated/distorted (user feedback: "looks bad")
3. **Architecture Limitation** - Single-GPU rendering won't scale for 54 shots at 4K

### 🔧 Solution Identified
**Multi-GPU Batch Rendering** - Split 54 shots across 2 GPUs (or 4 on better machine) for parallel processing

---

## 💻 SYSTEM SPECIFICATIONS

### Current Machine (2-GPU Setup)
- **GPUs:** 2x NVIDIA RTX A6000 (49GB VRAM each, 98GB total)
- **OS:** Linux 6.8.0-85-generic (Ubuntu 22.04)
- **CUDA:** 12.2
- **RAM:** Unknown (but sufficient for conda environment)
- **Storage:** ~110GB models + 39MB per rendered shot

### Target Machine (Tomorrow - 4-GPU Setup)
- **GPUs:** 4x GPUs (model/VRAM specs needed)
- **Benefits:**
  - 2x parallelization (4 shots simultaneously vs 2)
  - Better memory distribution for 4K renders
  - Faster completion (~90 mins vs 3+ hours)

---

## 📁 PROJECT STRUCTURE

```
/home/gogi/Desktop/Swavlamban 2025/
├── swav_offline_pipeline/              # MAIN PIPELINE (use this)
│   ├── orchestrate.py                  # Main render orchestrator (302 lines)
│   ├── storyboard.swav2025.yaml        # Original storyboard (54 shots, row_no based)
│   ├── storyboard.swav2025v2.yaml      # V2 storyboard (54 shots, id-based, 292 lines)
│   ├── environment.yml                 # Conda environment spec (fixed - no cudatoolkit)
│   ├── requirements.txt                # Python dependencies (26 packages)
│   ├── models_manifest.txt             # Required AI models list
│   ├── models/                         # Downloaded AI models (110GB)
│   │   ├── sdxl-base/                  # 72GB
│   │   ├── svd-img2vid/                # 31GB
│   │   ├── xtts-v2/                    # 2GB
│   │   └── musicgen-small/             # 5.5GB
│   ├── renders/swav2025/               # Output directory
│   │   └── intermediate/
│   │       └── shot_001.mp4            # ✅ COMPLETED (39MB, 4K, 7s)
│   ├── utils/
│   │   ├── models.py                   # AI model loaders (SDXL, SVD)
│   │   ├── audio.py                    # TTS synthesis, audio mixing
│   │   ├── video.py                    # Video effects, encoding
│   │   └── subtitles.py                # SRT caption generation
│   ├── scripts/
│   │   ├── setup.sh                    # Environment setup
│   │   ├── download_models.sh          # Model downloader
│   │   └── render.sh                   # Main render script (MODIFIED)
│   └── assets/                         # Supporting assets
├── swavlamban_offline_pipeline/        # Backup/alternate implementation
├── build_storyboard_yaml.py            # Generates YAML from JSON
├── storyboard_rows.json                # Source data (54 shots, 271 lines)
├── partial_media.xlsx                  # Media submissions from 16 companies
├── partial_media.csv                   # Google Drive links to real footage
├── monitor_progress.sh                 # ✅ NEW - Progress monitoring script
└── CLAUDE.md                           # ✅ THIS FILE - Session continuity doc
```

---

## 🎬 STORYBOARD STRUCTURE

### Total Shots: **54**
### Total Scenes: **15**

#### V2 YAML Structure (Recommended)
- **Format:** ID-based (`r001`, `r002`, etc.)
- **Methods:**
  - `t2v` (text-to-video) - SDXL generates still, then animated
  - `img2vid` - Stable Video Diffusion animates from base frame
  - `raw` - Process existing footage files
- **File:** `storyboard.swav2025v2.yaml` (292 lines)

#### Scenes Breakdown:
1. **Opening** (5 shots) - Event intro, NIIO overview
2. **Operational Readiness: Crew Safety & Damage Control** (4 shots)
3. **Undersea Robotics & Subsea Enablers** (5 shots)
4. **C4ISR: The Real-Time Maritime Picture** (3 shots)
5. **Autonomy at Sea** (3 shots)
6. **Aviation Safety & Ground Operations AI** (4 shots)
7. **Acoustics & ASW Enablers** (4 shots)
8. **Sensors & Silicon** (5 shots)
9. **Positioning When GNSS Is Denied** (4 shots)
10. **Harbour Turn-around & Shore Systems** (2 shots)
11. **Logistics & Persistent ISR** (4 shots)
12. **Special Operations & Deck-Edge Aids** (3 shots)
13. **Materials & Protective Systems** (2 shots)
14. **The Working Forum** (4 shots)
15. **Finale** (2 shots)

---

## 🔧 KEY FILES MODIFIED

### 1. `scripts/render.sh` (Lines 28-33)
**Changes Made:**
```bash
# REMOVED: export PYTHONNOUSERSITE=1  # (blocked user site-packages)
# REMOVED: export TRANSFORMERS_NO_TF=1
# REMOVED: export DIFFUSERS_SKIP_TF_IMPORT=1

# ADDED:
export TRANSFORMERS_OFFLINE=1
export HF_HUB_OFFLINE=1
export TF_CPP_MIN_LOG_LEVEL=3
unset TF_ENABLE_ONEDNN_OPTS
```

**Reason:** Fixed import errors for requests module and TensorFlow conflicts

### 2. `environment.yml` (Lines 1-8)
**Changes Made:**
```yaml
# REMOVED:
#   - nvidia
#   - cudatoolkit=12.1

# KEPT:
name: swav_offline
channels:
  - conda-forge
dependencies:
  - python=3.10
  - ffmpeg
  - git
  - pip
```

**Reason:** `cudatoolkit=12.1` package not available in conda; PyTorch provides CUDA libraries via pip

---

## 🐍 PYTHON ENVIRONMENT

### Conda Environment: `swav_offline`
**Location:** `/home/gogi/miniconda3/envs/swav_offline`

### Key Package Versions:
```
torch==2.4.0+cu121
torchvision==0.19.0+cu121
torchaudio==2.4.0+cu121
xformers==0.0.27.post2
diffusers==0.35.2
transformers==4.57.1
accelerate==1.10.1
TTS==0.22.0
numpy==1.22.0           # ⚠️ Conflict: TTS requires 1.22.0, diffusers needs 1.24+
opencv-python==4.11.0.86
pyyaml==6.0.3
rich==14.2.0
moviepy==1.0.3
ffmpeg-python==0.2.0
pydub==0.25.1
librosa==0.10.0
soundfile==0.13.1
huggingface_hub==0.35.3
```

### Known Dependency Conflicts (Non-blocking):
```
- numpy version mismatch (TTS vs diffusers) - RESOLVED via numpy==1.24.3 compromise
- TensorFlow removed entirely (not needed)
```

---

## 🎨 RENDERING WORKFLOW

### Current Single-GPU Process (FAILED at shot 2):
```
1. Load SDXL pipeline → GPU 0
2. Generate shot_001 (t2v method):
   - SDXL generates 3840x2160 still (30 steps @ 2.09s/step)
   - FFmpeg applies Ken Burns effect
   - Encode to H.264 → shot_001.mp4 (39MB, 7s)
3. Generate shot_002 (img2vid method):
   - SDXL generates base frame (25 steps @ 2.06s/step)
   - Load SVD pipeline
   - Animate 40 frames (25 steps @ 4.07s/step)
   - ❌ CUDA OOM ERROR at decode stage (tried to allocate 16.88GB, only 11.91GB free)
```

### Proposed Multi-GPU Batch Process:
```
GPU 0: Renders shots 1, 3, 5, 7... (odd numbers)
GPU 1: Renders shots 2, 4, 6, 8... (even numbers)
GPU 2: Renders shots 27-40           # On 4-GPU machine tomorrow
GPU 3: Renders shots 41-54           # On 4-GPU machine tomorrow

All GPUs run in parallel → 27 batches × ~2-3 mins = ~60-90 minutes total
```

---

## ⚙️ CUDA OUT-OF-MEMORY ANALYSIS

### Error Details:
```
torch.OutOfMemoryError: CUDA out of memory.
Tried to allocate 16.88 GiB.
GPU 0 has a total capacity of 47.43 GiB of which 11.91 GiB is free.
Including non-PyTorch memory, this process has 35.50 GiB memory in use.
Of the allocated memory 33.99 GiB is allocated by PyTorch, and 1.19 GiB is reserved by PyTorch but unallocated.
```

### Root Cause:
- **SDXL model:** ~7GB VRAM
- **SVD model:** ~17GB VRAM (loaded alongside SDXL)
- **4K video tensors:** ~10GB during decode
- **Total required:** ~34GB baseline + 16.88GB decode = **50.88GB** (exceeds 49GB GPU limit)

### Solutions:
1. **✅ Multi-GPU Split:** Render t2v on GPU 0, img2vid on GPU 1 (models isolated)
2. **✅ Lower Resolution:** Drop to 1080p (1920x1080) temporarily for testing
3. **✅ Reduce Batch Size:** Process fewer frames per decode chunk
4. **✅ CPU Offload:** Enable `enable_model_cpu_offload()` in models.py (slower but memory-safe)

---

## 🚀 NEXT SESSION TASKS (4-GPU Machine)

### Immediate Actions:
1. ✅ **Sync this CLAUDE.md to GitHub** (git add + commit + push)
2. ✅ **Verify environment on 4-GPU machine:**
   ```bash
   conda env list | grep swav_offline
   nvidia-smi
   ```
3. ✅ **Pull latest code:**
   ```bash
   cd "/home/gogi/Desktop/Swavlamban 2025"
   git pull origin main
   ```

### Create Batch Rendering Script:
```bash
# File: scripts/render_batch.sh
# Split shots across 4 GPUs

GPU 0: shots 1-14   (14 shots)
GPU 1: shots 15-28  (14 shots)
GPU 2: shots 29-41  (13 shots)
GPU 3: shots 42-54  (13 shots)
```

### Execution Plan:
```bash
# Terminal 1 (GPU 0)
CUDA_VISIBLE_DEVICES=0 python orchestrate.py --shots 1-14 --outdir renders/gpu0/

# Terminal 2 (GPU 1)
CUDA_VISIBLE_DEVICES=1 python orchestrate.py --shots 15-28 --outdir renders/gpu1/

# Terminal 3 (GPU 2)
CUDA_VISIBLE_DEVICES=2 python orchestrate.py --shots 29-41 --outdir renders/gpu2/

# Terminal 4 (GPU 3)
CUDA_VISIBLE_DEVICES=3 python orchestrate.py --shots 42-54 --outdir renders/gpu3/

# Monitor all 4 in parallel:
watch -n 30 'ls -lh renders/*/intermediate/*.mp4 | wc -l'
```

### Post-Render Tasks:
1. **Verify all 54 shots rendered**
2. **Manual stitching** (user preference - allows editing flexibility)
3. **Voiceover synthesis** (XTTS v2 - works independently)
4. **Audio mixing** (voiceover + music)
5. **SRT caption generation**
6. **Final master export** (H.264 or ProRes)

---

## 🎥 SHOT COMPLETION STATUS

### Completed: 1/54 (1.85%)

| Shot ID | Row | Method  | Duration | Status      | File Size | Issues |
|---------|-----|---------|----------|-------------|-----------|--------|
| r001    | 1   | t2v     | 7s       | ✅ DONE     | 39MB      | ⚠️ Quality concerns (pixelated backgrounds) |
| r002    | 2   | img2vid | 5s       | ❌ FAILED   | -         | CUDA OOM at 48% (12/25 steps) |
| r003-r054 | 3-54 | Mixed | ~5-7s   | ⏸️ PENDING | -         | Awaiting multi-GPU setup |

### Quality Assessment (User Feedback):
**shot_001.mp4:**
- ✅ Text overlays rendered correctly
- ✅ Encoding quality good (H.264, 4K @ 30fps)
- ❌ **Background quality poor** - "looks bad for real" - distorted pixel blocks
- ❌ **Not suitable for professional exhibition** in current form

**Recommendation:** Consider using real media from `partial_media.csv` (16 companies with Google Drive footage) instead of AI generation for final production.

---

## 📊 RENDERING PERFORMANCE METRICS

### Shot 001 (t2v - COMPLETED):
- **SDXL Inference:** 30 steps × 2.09s = 62.7s
- **FFmpeg Encoding:** ~10s
- **Total Time:** ~73s (~1.2 minutes)

### Shot 002 (img2vid - FAILED):
- **SDXL Base Frame:** 25 steps × 2.06s = 51.5s
- **SVD Animation:** 12/25 steps × 4.07s = 48.8s (crashed at 48%)
- **Total Before Crash:** ~100s (~1.7 minutes)

### Estimated Times:
- **Per Shot Average:** 2-3 minutes
- **54 Shots Single GPU:** 108-162 minutes (1.8-2.7 hours) **+ crashes**
- **54 Shots 2-GPU Parallel:** 54-81 minutes (0.9-1.35 hours) **if OOM resolved**
- **54 Shots 4-GPU Parallel:** 27-40 minutes (0.45-0.67 hours) **if OOM resolved**

---

## 🛠️ TROUBLESHOOTING GUIDE

### Issue 1: CUDA Out of Memory
**Symptoms:** `torch.OutOfMemoryError` during img2vid decode
**Solutions:**
```python
# Option A: Enable CPU offload (in utils/models.py)
pipe.enable_model_cpu_offload()

# Option B: Reduce decode chunk size (in orchestrate.py line ~118)
result = img2vid_pipe(..., decode_chunk_size=2)  # Default is 5

# Option C: Lower resolution temporarily
--preset hd  # 1920x1080 instead of 4k
```

### Issue 2: Missing Dependencies
**Symptoms:** `ModuleNotFoundError: No module named 'requests'`
**Solutions:**
```bash
# Ensure render.sh does NOT have PYTHONNOUSERSITE=1
# Install missing package:
conda activate swav_offline
pip install requests
```

### Issue 3: TensorFlow Import Errors
**Symptoms:** `Could not import module 'CLIPImageProcessor'`
**Solution:**
```bash
# Uninstall TensorFlow (not needed):
conda activate swav_offline
pip uninstall -y tensorflow tensorflow-gpu
```

### Issue 4: NumPy Version Conflicts
**Symptoms:** `numpy._core.multiarray failed to import`
**Solution:**
```bash
# Use compatible version:
pip install numpy==1.24.3 --force-reinstall
```

---

## 📝 ALTERNATIVE MEDIA SOURCES

### Real Footage Available (16 Companies):
Located in: `partial_media.csv`

| Company | Google Drive Link | Submitted |
|---------|------------------|-----------|
| Resonating Mindz Pvt.Ltd | [Link](https://drive.google.com/drive/folders/1-b1GUaTJ9DWm2AkCrqYV7_4hkmkiLqwb) | 15/10/2025 |
| CORATIA TECHNOLOGIES | [Link](https://drive.google.com/drive/u/1/folders/1lYLOZD0tyndIaWNg_MRl13ZaZC0HDRp4) | 10/10/2025 |
| Ci4 - Autonomous Defense | [Link](https://drive.google.com/drive/folders/1ba1KtL_IsLqGKPM_r1TdIgRSbMlHRjrt) | 10/10/2025 |
| ASP Innovative Solutions | [Link](https://drive.google.com/drive/folders/1MvuA0pFtOj4bpVb-JEBjECIHLdCf4iQ0) | 10/10/2025 |
| Azista Industries | [Link](https://drive.google.com/drive/folders/1DCOjnu8ORodUJBo8OjWzncloBqXTnN6m) | 10/10/2025 |
| AETHRONE AEROSPACE | [Link](https://drive.google.com/drive/folders/1STrglGiV-AIM6WmKwgCw2BBZyWSk0JTP) | 10/10/2025 |
| TARDID Technologies | [Link](https://drive.google.com/file/d/183O-WakKyT2-7gMCoKZjRA2WE6Q6xMSS) | 09/10/2025 |
| Planys Technologies | [Link](https://drive.google.com/drive/folders/16J2DIbmStBITkyuPpCO5oo0G_YdO3K_N) | 09/10/2025 |
| Combat Robotics India | [Link](https://drive.google.com/file/d/1ZgWRKndFR8eYlFBnsBQvaUDk4LqouWKY) | 08/10/2025 |
| EON SPACE LABS | [Link](https://drive.google.com/drive/folders/1DDYPD1aOpWm927SOlhEiBQNPFU-fvXoZ) | 08/10/2025 |
| Guardinger Advanced Tech | [Link](https://drive.google.com/drive/folders/1sUfhwzNpCn0jsDcWO1bg7YIsZ3XYu7PM) | 08/10/2025 |
| Kalbhorz Electric | [Link](https://drive.google.com/drive/folders/1JlJTOX2ukB7m3-XLTHUmZb6Y8DE85r0S) | 07/10/2025 |
| Medjay Technologies | [Link](https://drive.google.com/drive/folders/1MTJnPZrO8ei85YeUwEtUjhWj32P-swwO) | 07/10/2025 |
| Adisan Systems LLP | [Link](https://drive.google.com/drive/folders/17bRE-GSPsBk1k17LSovD8xFAuK-eStAe) | 03/10/2025 |
| IROV Technologies (EyeROV) | [Link](https://drive.google.com/drive/folders/14lGhXC43Is-XuCX5ts9Z88gSQ5OZLv0r) | 03/10/2025 |
| Saif Automations Services | [Link](https://drive.google.com/drive/folders/1qSd8EdqmdYVJBxlb_y1wZA6iuCYlVXkL) | 27/09/2025 |

**Note:** Consider hybrid approach - use real footage where available, AI generation for gaps/transitions only.

---

## 🔍 MONITORING & DEBUGGING

### Progress Monitor Script:
```bash
# Run anytime to check status:
bash monitor_progress.sh

# Output shows:
# - Shots completed (X/54)
# - Progress percentage
# - Latest completed shot
# - File sizes
```

### Log Files:
```
renders/swav2025/intermediate/   # Individual shot MP4 files
render_v2.log                    # Latest render attempt log
render_final.log                 # Previous render attempt
render_output.log                # Earlier attempts
```

### GPU Monitoring:
```bash
# Real-time GPU usage:
watch -n 1 nvidia-smi

# Check VRAM allocation:
nvidia-smi --query-gpu=index,memory.used,memory.free --format=csv

# Monitor PyTorch memory:
# Add to orchestrate.py:
import torch
print(torch.cuda.memory_summary(device=0))
```

---

## 📦 GIT REPOSITORY STATUS

**Repository:** Already initialized
**Branch:** `main`
**Remote:** `origin/main` (up to date)

### Untracked Files (Add before commit):
```
monitor_progress.sh              # ✅ NEW - Progress monitoring utility
swav_offline_pipeline/render_final.log
swav_offline_pipeline/render_v2.log
CLAUDE.md                        # ✅ THIS FILE
```

### Modified Files (Already tracked):
```
swav_offline_pipeline/scripts/render.sh        # Environment variables fixed
swav_offline_pipeline/environment.yml          # Removed cudatoolkit
```

### Commit Checklist Before Session End:
```bash
cd "/home/gogi/Desktop/Swavlamban 2025"
git add CLAUDE.md
git add monitor_progress.sh
git add swav_offline_pipeline/scripts/render.sh
git add swav_offline_pipeline/environment.yml
git commit -m "Session 2025-10-16: Multi-GPU batch setup + progress documentation

- Fixed CUDA OOM by identifying need for multi-GPU parallelization
- Completed shot_001 (39MB, 4K) but quality concerns noted
- Modified render.sh environment variables (removed PYTHONNOUSERSITE)
- Fixed environment.yml (removed unavailable cudatoolkit)
- Created CLAUDE.md for session continuity
- Created monitor_progress.sh for render tracking
- Ready for 4-GPU batch rendering tomorrow

Status: 1/54 shots complete, awaiting better hardware"

git push origin main
```

---

## 🎯 DECISION POINTS FOR TOMORROW

### Question 1: Continue AI Generation or Use Real Footage?
**AI Generation Pros:**
- ✅ Fully automated pipeline
- ✅ Consistent visual style
- ✅ Matches narration exactly

**AI Generation Cons:**
- ❌ Poor visual quality (pixelated backgrounds)
- ❌ High VRAM requirements
- ❌ Time-consuming (even with 4 GPUs)
- ❌ Not suitable for professional exhibition

**Real Footage Pros:**
- ✅ Professional quality
- ✅ Authentic equipment/products
- ✅ Faster editing workflow
- ✅ 16 companies already submitted media

**Real Footage Cons:**
- ❌ Manual editing required
- ❌ May not match all 54 shot descriptions
- ❌ Inconsistent lighting/quality across sources

**Recommendation:** Hybrid approach - use real footage as primary, AI for title cards/transitions only.

### Question 2: Resolution Strategy?
- **Option A:** Continue 4K (3840x2160) - requires multi-GPU + memory optimization
- **Option B:** Drop to 1080p (1920x1080) - faster, less memory, still HD quality
- **Option C:** Render 1080p first, upscale later with Real-ESRGAN

### Question 3: Batch Size?
- **54 shots / 4 GPUs = 13-14 shots per GPU**
- Each GPU processes sequentially, but all 4 run in parallel
- Estimated time: 27-40 minutes total

---

## 📚 REFERENCE COMMANDS

### Environment Activation:
```bash
source /home/gogi/miniconda3/etc/profile.d/conda.sh
conda activate swav_offline
```

### Full Render (Single GPU - NOT RECOMMENDED):
```bash
cd "/home/gogi/Desktop/Swavlamban 2025/swav_offline_pipeline"
bash scripts/render.sh
```

### Monitor Progress:
```bash
bash "/home/gogi/Desktop/Swavlamban 2025/monitor_progress.sh"
```

### View Completed Shot:
```bash
vlc "/home/gogi/Desktop/Swavlamban 2025/swav_offline_pipeline/renders/swav2025/intermediate/shot_001.mp4"
```

### Check GPU Status:
```bash
nvidia-smi
```

### Kill Stuck Processes:
```bash
pkill -9 python
pkill -9 -f orchestrate.py
```

---

## 🚨 CRITICAL NOTES FOR NEXT SESSION

1. **DO NOT run single-GPU render** - Will crash at shot 2 with OOM
2. **shot_001.mp4 quality is poor** - User confirmed "looks bad" - consider alternatives
3. **Environment is ready** - `swav_offline` conda env has all dependencies
4. **Models downloaded** - 110GB in `swav_offline_pipeline/models/` (don't re-download)
5. **Git repo clean** - Commit CLAUDE.md before session ends
6. **4-GPU machine required** - Current 2-GPU system insufficient for 4K rendering

---

## 📞 CONTACT & CONTEXT

**Exhibition Date:** 25-26 November 2025 (39 days away as of 2025-10-16)
**Organizer:** Naval Innovation & Indigenisation Organisation (NIIO)
**Final Deliverable:** Professional 4K exhibition film (~5-7 minutes total duration)

**This document was generated by Claude (Anthropic) to ensure session continuity across hardware transitions.**

---

**End of Session Report - Continue from here tomorrow on 4-GPU machine** 🚀
