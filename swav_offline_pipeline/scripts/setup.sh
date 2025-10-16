#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! command -v conda >/dev/null 2>&1; then
  echo "[ERROR] conda command not found. Please install Miniconda or Anaconda before running this script."
  exit 1
fi

echo "========== STEP 1: System prerequisites =========="
echo "Installing system dependencies (sudo password may be required)..."
sudo apt-get update
sudo apt-get install -y ffmpeg libsndfile1 git

eval "$(conda shell.bash hook)"

ENV_NAME="$(awk -F': ' '$1 == \"name\" {print $2}' \"$ROOT_DIR/environment.yml\")"

echo
echo "========== STEP 2: Conda environment =========="
if conda env list | awk '{print $1}' | grep -Fxq "$ENV_NAME"; then
  echo "Conda environment '$ENV_NAME' already exists. Skipping creation."
else
  echo "Creating conda environment '$ENV_NAME'..."
  conda env create -f "$ROOT_DIR/environment.yml"
fi

conda activate "$ENV_NAME"

echo
echo "========== STEP 3: Python packages =========="
echo "Installing Python requirements..."
pip install --upgrade pip
pip install -r "$ROOT_DIR/requirements.txt"

echo
echo "========== STEP 4: CUDA sanity check =========="
python - <<'PY'
import torch

print(f"torch version: {torch.__version__}")
print(f"cuda available: {torch.cuda.is_available()}")
print(f"cuda device count: {torch.cuda.device_count()}")
if torch.cuda.is_available():
    for idx in range(torch.cuda.device_count()):
        print(f"gpu {idx}: {torch.cuda.get_device_name(idx)}")
PY

echo
echo "========== DONE =========="
echo "Environment setup complete."
