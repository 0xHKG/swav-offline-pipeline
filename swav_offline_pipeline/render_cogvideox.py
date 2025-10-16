#!/usr/bin/env python3
"""
CogVideoX-5B renderer for Swavlamban 2025
Much better quality than SDXL+SVD
"""

import argparse
import os
from pathlib import Path
import yaml
import torch
import numpy as np
from rich.console import Console
from diffusers import CogVideoXPipeline
from diffusers.utils import export_to_video

console = Console()

PRESET_RESOLUTIONS = {
    "480p": (720, 480),   # CogVideoX native
    "720p": (1280, 720),  # Upscaled
    "1080p": (1920, 1080) # Upscaled
}

def load_shot_from_yaml(storyboard_path: str, shot_id: str):
    """Load specific shot by ID from storyboard v2"""
    with open(storyboard_path, 'r') as f:
        data = yaml.safe_load(f)

    for scene in data.get('scenes', []):
        for shot in scene.get('shots', []):
            if shot.get('id') == shot_id:
                return shot

    raise ValueError(f"Shot {shot_id} not found")

def render_shot(shot, width, height, fps, out_path):
    """Render using CogVideoX-5B"""
    console.print(f"[bold cyan]Rendering {shot['id']} with CogVideoX-5B[/bold cyan]")

    model_path = Path(__file__).parent / "models" / "cogvideox-5b"

    # Load pipeline
    console.print(f"[yellow]Loading CogVideoX pipeline...[/yellow]")
    pipe = CogVideoXPipeline.from_pretrained(
        str(model_path),
        torch_dtype=torch.float16
    )
    pipe.enable_model_cpu_offload()
    pipe.vae.enable_slicing()  # Correct method for CogVideoX VAE

    # Generate video
    prompt = shot['prompt']
    console.print(f"[cyan]Prompt: {prompt[:100]}...[/cyan]")

    video = pipe(
        prompt=prompt,
        num_videos_per_prompt=1,
        num_inference_steps=50,
        num_frames=49,  # 49 frames = 6 seconds @ 8fps native
        guidance_scale=6.0,
        height=480,
        width=720,
    ).frames[0]

    # Export to video
    console.print(f"[green]Exporting to {out_path}...[/green]")
    export_to_video(video, str(out_path), fps=fps)

    console.print(f"[bold green]✓ {shot['id']} complete![/bold green]")

def main():
    parser = argparse.ArgumentParser(description="Render with CogVideoX-5B")
    parser.add_argument("--storyboard", required=True)
    parser.add_argument("--shot-id", required=True)
    parser.add_argument("--outdir", required=True)
    parser.add_argument("--preset", default="480p", choices=["480p", "720p", "1080p"])

    args = parser.parse_args()

    out_dir = Path(args.outdir)
    inter_dir = out_dir / "intermediate"
    inter_dir.mkdir(parents=True, exist_ok=True)

    width, height = PRESET_RESOLUTIONS[args.preset]
    fps = 30

    shot = load_shot_from_yaml(args.storyboard, args.shot_id)
    out_path = inter_dir / f"{args.shot_id}.mp4"

    render_shot(shot, width, height, fps, out_path)

    return 0

if __name__ == "__main__":
    exit(main())
