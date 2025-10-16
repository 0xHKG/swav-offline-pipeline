#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODELS_DIR="${ROOT_DIR}/models"

mkdir -p "${MODELS_DIR}"

declare -A REPOS=(
  ["sdxl-base"]="stabilityai/stable-diffusion-xl-base-1.0"
  ["svd-img2vid"]="stabilityai/stable-video-diffusion-img2vid-xt"
  ["xtts-v2"]="coqui/XTTS-v2"
  ["musicgen-small"]="facebook/musicgen-small"
)

echo "========== MODEL DOWNLOAD =========="
echo "Target directory: ${MODELS_DIR}"
for target in "${!REPOS[@]}"; do
  repo="${REPOS[$target]}"
  out_dir="${MODELS_DIR}/${target}"
  if [ -d "${out_dir}" ] && [ -n "$(ls -A "${out_dir}" 2>/dev/null)" ]; then
    echo "• ${repo} already present at ${out_dir}, skipping."
    continue
  fi
  echo "• Fetching ${repo} → ${out_dir}"
  if ! huggingface-cli download "${repo}" --local-dir "${out_dir}" --local-dir-use-symlinks False; then
    echo "⚠️  Failed to download ${repo}. If a license or EULA is required, please run 'huggingface-cli login' and accept the terms in your browser."
  fi
done

mkdir -p "${MODELS_DIR}/realesrgan" "${MODELS_DIR}/rife"
if [ ! -f "${MODELS_DIR}/realesrgan/README.md" ]; then
  cat > "${MODELS_DIR}/realesrgan/README.md" <<'EOF'
Optional Real-ESRGAN weights can be placed here.
EOF
fi
if [ ! -f "${MODELS_DIR}/rife/README.md" ]; then
  cat > "${MODELS_DIR}/rife/README.md" <<'EOF'
Optional RIFE interpolation weights can be placed here.
EOF
fi

echo "========== COMPLETE =========="
