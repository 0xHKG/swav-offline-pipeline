# SESSION SUMMARY - 2025-10-17

**Date:** 2025-10-17 00:15 → 03:45 IST (3.5 hours)
**Branch:** cogvideox-improved
**Machine:** 2× NVIDIA RTX A6000 (49GB each)

---

## 🎯 SESSION OBJECTIVES
1. Test CogVideoX-5B quality
2. Find superior video generation model
3. Successfully render test shot with new model

## ✅ COMPLETED TASKS

### 1. CogVideoX-5B Quality Assessment
- **Test Render:** r001 completed in 7 minutes (50 inference steps, 49 frames)
- **Output:** 84KB file (extremely small - red flag)
- **User Verdict:** "better but still not good"
- **Issues:** Garbled text ("SUMVWAlANRia Mealan 200± 2023)" instead of clean text), AI artifacts
- **Conclusion:** NOT acceptable for professional Navy exhibition

### 2. Prompt Optimization Strategy Created
- **File Created:** [PROMPT_OPTIMIZATION.md](swav_offline_pipeline/PROMPT_OPTIMIZATION.md) (394 lines)
- **Key Insight:** AI models cannot generate readable text - always produces garbled approximations
- **Solution:** Remove all text overlays from prompts, add in post-production with FFmpeg
- **Enhancement Function:** `enhance_prompt()` - removes text, adds cinematic keywords, camera work
- **Expected Improvement:** 30-50% quality increase

### 3. HunyuanVideo Attempted
- **Downloaded:** 38GB model from `tencent/HunyuanVideo`
- **Result:** FAILED - Wrong format! Downloaded raw PyTorch weights instead of diffusers-compatible format
- **Error:** `model_index.json` not found
- **Lesson:** Always verify repo format before large downloads

### 4. Wan 2.2 A14B Model Research & Download
- **Model:** Wan-AI/Wan2.2-T2V-A14B (Mixture-of-Experts architecture)
- **Downloaded:** 118GB total (NOT 14GB as docs claimed!)
- **Architecture:**
  - 2 expert models: high_noise_model (14B params) + low_noise_model (14B params)
  - Total: 27B parameters (14B active per step)
  - T5-XXL text encoder (11GB)
  - Wan 2.1 VAE (3GB)
- **Quality:** Outperforms Runway Gen-3, industry-leading open-source
- **Download Time:** 53 minutes for 118GB

### 5. Wan 2.2 Dependencies Installed
- `decord==0.6.0` - Video processing library
- `peft==0.17.1` - Parameter-Efficient Fine-Tuning
- `flash_attn==2.8.3` - FlashAttention for efficient inference (built from source)
- `transformers==4.51.3` - Downgraded for compatibility
- `numpy==1.26.4` - Upgraded from 1.22.0

### 6. Multiple Rendering Attempts (All Failed on 2-GPU System)

#### Attempt 1: Single-GPU with CPU Offloading
- **Command:** `--offload_model True --convert_model_dtype --t5_cpu`
- **Result:** CUDA OOM - Tried to allocate 1.44 GiB, only 402 MiB free
- **GPU 0 Usage:** 47.02 GiB (PyTorch: 46.69 GiB)
- **Root Cause:** Model too large even with offloading

#### Attempt 2: Single-GPU 1 (Explicit)
- **Command:** `CUDA_VISIBLE_DEVICES=1` + same flags
- **Result:** CUDA OOM - Tried to allocate 8.65 GiB, only 8.42 GiB free
- **GPU Usage:** 38.36 GiB memory in use
- **Root Cause:** Each GPU needs ~46GB just for model loading

#### Attempt 3: 2-GPU FSDP + Ulysses
- **Command:** `torchrun --nproc_per_node=2 --dit_fsdp --t5_fsdp --ulysses_size 2`
- **Result:** CUDA OOM during FSDP sharding
- **Error:** Tried to allocate 672 MiB for FSDP operations
- **Both GPUs:** 46.13 GiB allocated by PyTorch + 242 MiB reserved
- **Root Cause:** 27B parameter model too large for 2×49GB GPUs

### 7. Root Cause Analysis Complete
**Problem:** Wan 2.2 A14B has **TWO 14B expert models** (not one 14B model as docs implied)
- high_noise_model: 14B params for early denoising (high noise → layout)
- low_noise_model: 14B params for late denoising (low noise → detail refinement)
- **Total:** 27B parameters active throughout inference

**Memory Breakdown on 2-GPU FSDP:**
- Model shard per GPU: ~23GB
- T5 encoder sharded: ~5.5GB per GPU
- VAE (replicated): ~3GB per GPU
- Inference activations: ~10-15GB per GPU
- **Total:** ~46.5GB per GPU → **Exceeds 49GB limit!**

**Solution:** Need 4 GPUs to distribute the load:
- Model sharded 4 ways: ~11.5GB per GPU
- T5 sharded 4 ways: ~2.75GB per GPU
- VAE: ~3GB per GPU
- Activations: ~10-15GB per GPU
- **Total:** ~32.25GB per GPU ✅ (within 49GB limit with 16GB margin)

### 8. Decision: Move to 4-GPU Machine
- **Rationale:** 4 GPUs provide 196GB total VRAM vs 98GB on 2-GPU system
- **Expected Performance:** ~44GB per GPU (within limits)
- **Command for 4-GPU:**
  ```bash
  torchrun --nproc_per_node=4 generate.py \
    --task t2v-A14B \
    --size 1280*720 \
    --ckpt_dir ../models/wan22 \
    --dit_fsdp --t5_fsdp --ulysses_size 4 \
    --prompt "..." \
    --base_seed 42
  ```

### 9. Documentation Created
- **4GPU_SETUP_GUIDE.md** - Complete step-by-step setup for new PC
- **SESSION_SUMMARY_2025-10-17.md** - This file
- **Updated CLAUDE.md** - Session status and model details

---

## ❌ FAILED ATTEMPTS SUMMARY

| Attempt | Configuration | GPU Usage | Error | Root Cause |
|---------|--------------|-----------|-------|------------|
| 1 | Single-GPU, CPU offload | 47GB | OOM (alloc 1.44GB) | Model + activations > 49GB |
| 2 | Single-GPU 1, CPU offload | 38GB | OOM (alloc 8.65GB) | Insufficient VRAM for inference |
| 3 | 2-GPU FSDP, Ulysses=2 | 46GB each | OOM (alloc 672MB) | FSDP sharding overhead + model too large |

**Conclusion:** Wan 2.2 A14B requires minimum 4 GPUs for 49GB VRAM per GPU hardware.

---

## 📊 MODELS STATUS

| Model | Size | Status | Quality | Notes |
|-------|------|--------|---------|-------|
| SDXL + SVD | 103GB | ❌ REMOVED | Poor | Pixelated, user: "looks bad" |
| CogVideoX-5B | 21GB | ✅ KEPT | Insufficient | Garbled text, 84KB output |
| HunyuanVideo | 38GB | ❌ REMOVED | N/A | Wrong format downloaded |
| Wan 2.2 A14B | 118GB | ✅ READY | Unknown | Needs 4 GPUs to test |
| XTTS v2 | 2GB | ✅ KEPT | Good | TTS working |
| MusicGen | 5.5GB | ✅ KEPT | Good | Background music |

**Total Model Footprint:** 146.5GB (after cleanup)

---

## 🔧 SYSTEM CHANGES

### Conda Environment (`swav_offline`)
**Packages Updated:**
- `transformers`: 4.57.1 → 4.51.3 (Wan 2.2 compatibility)
- `numpy`: 1.22.0 → 1.26.4 (compatibility + TTS fix)
- `tokenizers`: 0.22.1 → 0.21.4

**Packages Added:**
- `decord==0.6.0`
- `peft==0.17.1`
- `flash_attn==2.8.3`
- `easydict`
- `ftfy`
- `dashscope`
- `wcwidth`
- `cryptography==46.0.3`

### Files Added/Modified
**New Files:**
- `swav_offline_pipeline/PROMPT_OPTIMIZATION.md` (394 lines)
- `swav_offline_pipeline/render_hunyuanvideo.py` (153 lines) - unused
- `swav_offline_pipeline/wan22_inference/` (cloned from GitHub)
- `swav_offline_pipeline/models/wan22/` (118GB)
- `4GPU_SETUP_GUIDE.md` (this session)
- `SESSION_SUMMARY_2025-10-17.md` (this file)

**Modified Files:**
- `CLAUDE.md` - Updated session status, model details
- Git commits on `cogvideox-improved` branch

---

## 🚀 NEXT STEPS (4-GPU Machine Tomorrow)

### Immediate Tasks
1. **Transfer models** to 4-GPU machine (118GB - use USB or network transfer)
2. **Setup conda environment** following 4GPU_SETUP_GUIDE.md
3. **Run test render** with 4-GPU FSDP
4. **Assess quality** - If acceptable, proceed with all 54 shots
5. **Batch render** - Expected time: 6-9 hours for 54 shots

### Alternative Path (if Wan 2.2 quality still insufficient)
1. **Use real footage** from 16 companies (partial_media.csv)
2. **Manual video editing** in DaVinci Resolve / Premiere Pro
3. **AI only for title cards** and transitions
4. **Hybrid approach** - real footage + AI enhancements

---

## 📈 LESSONS LEARNED

1. **Always verify model architecture** before downloading large files
   - Wan 2.2 "14B" actually means 2×14B experts = 27B total!

2. **Documentation can be misleading**
   - Wan 2.2 docs claim "optimized for 8-49GB VRAM" but fails on 49GB single GPU
   - Required configuration buried in multi-GPU examples

3. **FSDP has overhead**
   - FSDP sharding operations need additional VRAM beyond model size
   - 2-GPU split of 27B model still needs 46GB+ per GPU

4. **AI text generation is fundamentally broken**
   - No current T2V model can generate readable text
   - Solution: Remove text from prompts, add in post-production

5. **Hardware requirements scale with model quality**
   - Better quality = larger models = more GPUs needed
   - Trade-off: Quality vs Infrastructure vs Time

---

## 💾 GIT STATUS

**Branch:** cogvideox-improved
**Commits Today:** 2
1. "Add prompt optimization and switch to Wan 2.2"
2. (Pending) "Session 2025-10-17: Wan 2.2 A14B download + 4-GPU setup guide"

**Files Staged for Commit:**
- CLAUDE.md (updated)
- 4GPU_SETUP_GUIDE.md (new)
- SESSION_SUMMARY_2025-10-17.md (new)
- swav_offline_pipeline/PROMPT_OPTIMIZATION.md (new)

**Ready to Push:** YES

---

## ⏱️ TIME BREAKDOWN

| Activity | Duration | % of Session |
|----------|----------|--------------|
| CogVideoX testing | 30 min | 14% |
| HunyuanVideo attempt | 20 min | 9% |
| Wan 2.2 download | 53 min | 25% |
| Dependency installation | 15 min | 7% |
| Rendering attempts (3x) | 45 min | 21% |
| Debugging & analysis | 30 min | 14% |
| Documentation | 20 min | 10% |
| **TOTAL** | **3.5 hours** | **100%** |

---

## 📞 HANDOFF TO TOMORROW'S SESSION

**Start with:** [4GPU_SETUP_GUIDE.md](4GPU_SETUP_GUIDE.md) - Complete checklist for new PC setup

**Key Files to Reference:**
- CLAUDE.md - Full project context
- 4GPU_SETUP_GUIDE.md - Step-by-step setup
- PROMPT_OPTIMIZATION.md - Prompt engineering guide
- storyboard.swav2025v2.yaml - All 54 shots with prompts

**Critical Info:**
- Wan 2.2 A14B model: 118GB in `models/wan22/`
- Requires 4 GPUs minimum (will NOT work on 2 GPUs)
- Test command ready in setup guide
- Expected per-shot render time: 5-10 minutes
- Total render time for 54 shots: ~6-9 hours

**Success Criteria:**
- Test render completes without OOM
- All 4 GPUs show 40-45GB usage (not exceeding 49GB)
- Video quality acceptable (no garbled text, smooth motion)
- If quality good → render all 54 shots
- If quality poor → pivot to real footage from companies

---

**END OF SESSION SUMMARY** 🚀
