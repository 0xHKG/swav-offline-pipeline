#!/usr/bin/env bash
set -euo pipefail
sudo apt-get update -y
sudo apt-get install -y ffmpeg libsndfile1 git
conda env remove -n swavfilm -y || true
conda env create -f environment.yml
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate swavfilm
python - <<'PY'
import torch
print(torch.__version__, torch.cuda.is_available(), torch.cuda.device_count())
PY
pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cu121
echo "Env ready: conda activate swavfilm"
