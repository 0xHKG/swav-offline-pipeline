#!/usr/bin/env bash
set -euo pipefail
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate swavfilm
python orchestrate.py --storyboard storyboard.swav2025.yaml --outdir renders/swav2025 --gpus 0,1 --preset 4k --master h264
