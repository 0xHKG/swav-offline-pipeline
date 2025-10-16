from __future__ import annotations

from pathlib import Path
from typing import Optional

import torch
from diffusers import StableDiffusionXLPipeline, StableVideoDiffusionPipeline

MODEL_ROOT = Path(__file__).resolve().parents[1] / "models"

_SDXL_PIPE: Optional[StableDiffusionXLPipeline] = None
_SVD_PIPE: Optional[StableVideoDiffusionPipeline] = None


def _resolve_model_dir(name: str) -> Path:
    path = MODEL_ROOT / name
    if not path.exists():
        raise FileNotFoundError(f"Model directory not found: {path}")
    return path


def get_t2i() -> StableDiffusionXLPipeline:
    """Load SDXL pipeline once and enable CPU offload for memory efficiency."""
    global _SDXL_PIPE
    if _SDXL_PIPE is None:
        model_dir = _resolve_model_dir("sdxl-base")
        _SDXL_PIPE = StableDiffusionXLPipeline.from_pretrained(
            model_dir,
            torch_dtype=torch.float16,
            variant="fp16",
            use_safetensors=True,
            local_files_only=True,
        )
        _SDXL_PIPE.enable_model_cpu_offload()
    return _SDXL_PIPE


def get_img2vid() -> StableVideoDiffusionPipeline:
    """Load Stable Video Diffusion img2vid XT pipeline with CPU offload."""
    global _SVD_PIPE
    if _SVD_PIPE is None:
        model_dir = _resolve_model_dir("svd-img2vid")
        _SVD_PIPE = StableVideoDiffusionPipeline.from_pretrained(
            model_dir,
            torch_dtype=torch.float16,
            local_files_only=True,
        )
        _SVD_PIPE.enable_model_cpu_offload()
    return _SVD_PIPE
