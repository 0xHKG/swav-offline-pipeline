# 4-GPU MACHINE SETUP GUIDE - WAN 2.2 A14B

**Project:** Swavlamban 2025 AI Video Generation Pipeline
**Date Created:** 2025-10-17 03:45 IST
**Target Hardware:** 4× NVIDIA RTX A6000 (49GB VRAM each, 196GB total)

---

## 📋 COMPLETE TODO LIST FOR NEW PC SETUP

### Phase 1: System Verification (5 minutes)
- [ ] **1.1** Verify 4 GPUs are detected: `nvidia-smi`
- [ ] **1.2** Verify CUDA 12.2 installed: `nvcc --version`
- [ ] **1.3** Check available disk space (need 150GB free): `df -h`
- [ ] **1.4** Verify Git installed: `git --version`
- [ ] **1.5** Verify Miniconda/Anaconda installed: `conda --version`

### Phase 2: Clone Repository (5 minutes)
- [ ] **2.1** Navigate to workspace:
  ```bash
  cd ~/Desktop
  ```
- [ ] **2.2** Clone project repository:
  ```bash
  git clone https://github.com/0xHKG/swav-offline-pipeline.git "Swavlamban 2025"
  cd "Swavlamban 2025"
  ```
- [ ] **2.3** Checkout correct branch:
  ```bash
  git checkout cogvideox-improved
  ```
- [ ] **2.4** Pull latest changes:
  ```bash
  git pull origin cogvideox-improved
  ```

### Phase 3: Create Conda Environment (15 minutes)
- [ ] **3.1** Create environment from YAML:
  ```bash
  conda env create -f swav_offline_pipeline/environment.yml
  ```
- [ ] **3.2** Activate environment:
  ```bash
  source ~/miniconda3/etc/profile.d/conda.sh
  conda activate swav_offline
  ```
- [ ] **3.3** Install PyTorch with CUDA 12.1 support:
  ```bash
  pip install torch==2.4.0+cu121 torchvision==0.19.0+cu121 torchaudio==2.4.0+cu121 --index-url https://download.pytorch.org/whl/cu121
  ```
- [ ] **3.4** Install core dependencies:
  ```bash
  cd swav_offline_pipeline
  pip install -r requirements.txt
  ```
- [ ] **3.5** Install Wan 2.2 specific dependencies:
  ```bash
  pip install decord==0.6.0 peft==0.17.1 flash_attn==2.8.3 easydict ftfy dashscope
  ```
- [ ] **3.6** Verify installation:
  ```bash
  python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'GPUs: {torch.cuda.device_count()}')"
  ```
  Expected output:
  ```
  PyTorch: 2.4.0+cu121
  CUDA Available: True
  GPUs: 4
  ```

### Phase 4: Copy AI Models from Current Machine (2-3 hours)
**IMPORTANT:** Transfer models from current 2-GPU machine to avoid re-downloading 118GB!

#### Option A: Network Transfer (if machines on same network)
- [ ] **4.1** On current machine, compress models:
  ```bash
  cd "/home/gogi/Desktop/Swavlamban 2025/swav_offline_pipeline"
  tar -czf wan22_models.tar.gz models/wan22/ models/cogvideox-5b/ models/xtts-v2/ models/musicgen-small/
  ```
- [ ] **4.2** Transfer via rsync (replace <NEW_PC_IP> with actual IP):
  ```bash
  rsync -avz --progress wan22_models.tar.gz gogi@<NEW_PC_IP>:~/Desktop/
  ```
- [ ] **4.3** On new machine, extract:
  ```bash
  cd ~/Desktop/Swavlamban\ 2025/swav_offline_pipeline
  tar -xzf ~/Desktop/wan22_models.tar.gz
  ```

#### Option B: USB Drive Transfer (if no network)
- [ ] **4.1** On current machine, copy to USB:
  ```bash
  cp -r "/home/gogi/Desktop/Swavlamban 2025/swav_offline_pipeline/models" /media/gogi/USB_DRIVE/
  ```
- [ ] **4.2** On new machine, copy from USB:
  ```bash
  cp -r /media/gogi/USB_DRIVE/models ~/Desktop/Swavlamban\ 2025/swav_offline_pipeline/
  ```

#### Option C: Re-download from scratch (if transfer fails)
- [ ] **4.3** Download Wan 2.2 A14B (118GB, ~2-3 hours):
  ```bash
  cd ~/Desktop/Swavlamban\ 2025/swav_offline_pipeline
  conda activate swav_offline
  huggingface-cli download Wan-AI/Wan2.2-T2V-A14B --local-dir models/wan22 --local-dir-use-symlinks False
  ```

### Phase 5: Clone Wan 2.2 Inference Code (2 minutes)
- [ ] **5.1** Clone Wan 2.2 repository:
  ```bash
  cd ~/Desktop/Swavlamban\ 2025/swav_offline_pipeline
  git clone https://github.com/Wan-Video/Wan2.2.git wan22_inference
  ```
- [ ] **5.2** Verify structure:
  ```bash
  ls -la wan22_inference/generate.py
  ```

### Phase 6: Test Wan 2.2 with 4-GPU FSDP (10-15 minutes)
- [ ] **6.1** Run test generation:
  ```bash
  cd ~/Desktop/Swavlamban\ 2025/swav_offline_pipeline/wan22_inference
  conda activate swav_offline

  torchrun --nproc_per_node=4 generate.py \
    --task t2v-A14B \
    --size 1280*720 \
    --ckpt_dir ../models/wan22 \
    --dit_fsdp --t5_fsdp --ulysses_size 4 \
    --prompt "Indian Navy crest over the Tricolour, slow pan to the facade of Manekshaw Centre, cinematic documentary style, professional composition, photorealistic 4K footage, sharp focus, high detail" \
    --base_seed 42
  ```
- [ ] **6.2** Monitor GPU usage in separate terminal:
  ```bash
  watch -n 1 nvidia-smi
  ```
  Expected: All 4 GPUs showing 40-45GB VRAM usage each
- [ ] **6.3** Wait for completion (~5-10 minutes for first video)
- [ ] **6.4** Verify output file created:
  ```bash
  ls -lh *.mp4
  ```
- [ ] **6.5** Review video quality

### Phase 7: Create Production Rendering Script (5 minutes)
- [ ] **7.1** Create batch render script:
  ```bash
  cat > ~/Desktop/Swavlamban\ 2025/swav_offline_pipeline/wan22_inference/render_all_54_shots.sh << 'EOF'
#!/bin/bash
# Wan 2.2 A14B 4-GPU Batch Rendering Script
# Renders all 54 shots with FSDP + Ulysses parallelization

set -e

# Activate environment
source ~/miniconda3/etc/profile.d/conda.sh
conda activate swav_offline

# Change to inference directory
cd "$(dirname "$0")"

# Load storyboard (you'll need to parse this)
STORYBOARD="../storyboard.swav2025v2.yaml"

# Loop through all 54 shots
for i in $(seq -f "%03g" 1 54); do
  SHOT_ID="r${i}"
  echo "========================================"
  echo "Rendering shot ${SHOT_ID}"
  echo "========================================"

  # Extract prompt from storyboard (simplified - needs actual YAML parsing)
  PROMPT="Shot ${SHOT_ID} from Swavlamban 2025 exhibition film"

  # Render with 4-GPU FSDP
  torchrun --nproc_per_node=4 generate.py \
    --task t2v-A14B \
    --size 1280*720 \
    --ckpt_dir ../models/wan22 \
    --dit_fsdp --t5_fsdp --ulysses_size 4 \
    --prompt "${PROMPT}" \
    --base_seed ${i} \
    --save_file "../renders/wan22_shots/${SHOT_ID}.mp4"

  echo "✓ Completed shot ${SHOT_ID}"
  echo ""
done

echo "ALL 54 SHOTS RENDERED!"
EOF

  chmod +x ~/Desktop/Swavlamban\ 2025/swav_offline_pipeline/wan22_inference/render_all_54_shots.sh
  ```

### Phase 8: Verify Everything Works (5 minutes)
- [ ] **8.1** Test environment activation:
  ```bash
  conda activate swav_offline
  python -c "import torch, diffusers, transformers; print('All imports OK')"
  ```
- [ ] **8.2** Verify models accessible:
  ```bash
  ls -lh ~/Desktop/Swavlamban\ 2025/swav_offline_pipeline/models/wan22/
  ```
- [ ] **8.3** Check Git status:
  ```bash
  cd ~/Desktop/Swavlamban\ 2025
  git status
  ```

---

## 🚀 PRODUCTION RENDERING WORKFLOW

### Quick Start Command (After Setup Complete)
```bash
# Activate environment
source ~/miniconda3/etc/profile.d/conda.sh
conda activate swav_offline

# Navigate to inference directory
cd ~/Desktop/Swavlamban\ 2025/swav_offline_pipeline/wan22_inference

# Run single test shot
torchrun --nproc_per_node=4 generate.py \
  --task t2v-A14B \
  --size 1280*720 \
  --ckpt_dir ../models/wan22 \
  --dit_fsdp --t5_fsdp --ulysses_size 4 \
  --prompt "YOUR_PROMPT_HERE" \
  --base_seed 42

# Run all 54 shots (after testing)
bash render_all_54_shots.sh
```

### Expected Performance
- **Per Shot Render Time:** 5-10 minutes (first shot slower due to model loading)
- **Total Time for 54 Shots:** ~6-9 hours (sequential)
- **GPU Memory Usage:** ~44GB per GPU (within 49GB limit)
- **Output:** 1280×720 @ 16fps, 81 frames = 5 seconds per shot

---

## 📊 MEMORY BREAKDOWN (4-GPU FSDP)

| Component | Total Size | Per GPU (÷4) |
|-----------|------------|--------------|
| High-Noise Expert Model | ~14GB | ~3.5GB |
| Low-Noise Expert Model | ~14GB | ~3.5GB |
| T5-XXL Text Encoder | ~11GB | ~2.75GB |
| VAE Decoder | ~3GB | ~3GB (replicated) |
| Inference Activations | ~60GB | ~15GB |
| FSDP Overhead | ~20GB | ~5GB |
| **TOTAL** | **~122GB** | **~32.75GB per GPU** ✅ |

With 49GB per GPU available, we have **~16GB safety margin** per GPU!

---

## 🔧 TROUBLESHOOTING

### Issue: "CUDA out of memory" on 4 GPUs
**Diagnosis:** Should NOT happen if following this guide
**Solutions:**
1. Reduce resolution: `--size 832*480` (480p)
2. Add CPU offloading: `--offload_model True --convert_model_dtype --t5_cpu`
3. Verify only 4 GPUs visible: `echo $CUDA_VISIBLE_DEVICES` (should be empty)

### Issue: "torch.distributed timeout"
**Solution:** Increase timeout:
```bash
export NCCL_TIMEOUT=1800  # 30 minutes
```

### Issue: Slow first render
**Expected:** First video takes 2-3× longer due to model compilation (FlashAttention, CUDA kernels)
**Solution:** Wait it out - subsequent renders will be faster

---

## 📝 ESTIMATED TIMELINE

| Phase | Time | Status |
|-------|------|--------|
| System Verification | 5 min | ⏸️ Pending |
| Clone Repository | 5 min | ⏸️ Pending |
| Create Conda Environment | 15 min | ⏸️ Pending |
| Copy Models from Current PC | 30 min - 3 hrs | ⏸️ Pending |
| Clone Wan 2.2 Inference | 2 min | ⏸️ Pending |
| Test 4-GPU Rendering | 15 min | ⏸️ Pending |
| Create Production Script | 5 min | ⏸️ Pending |
| Verify Everything | 5 min | ⏸️ Pending |
| **TOTAL SETUP TIME** | **45 min - 4 hrs** | ⏸️ Pending |

---

## ✅ SUCCESS CRITERIA

Setup is complete when:
1. ✅ `conda activate swav_offline` works
2. ✅ `nvidia-smi` shows 4 GPUs
3. ✅ Test render completes without OOM errors
4. ✅ All 4 GPUs show 40-45GB usage during render
5. ✅ Output video file `*.mp4` is created and playable
6. ✅ Video quality is acceptable (no garbled text, smooth motion)

---

**CONTINUE TO NEXT PAGE FOR SESSION UPDATE AND COMMIT INSTRUCTIONS** →
