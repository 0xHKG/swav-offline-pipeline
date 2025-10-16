#!/usr/bin/env python3
"""
HunyuanVideo renderer for Swavlamban 2025
Industry-leading cinematic quality for professional exhibition
"""

import argparse
import os
from pathlib import Path
import yaml
import torch
from rich.console import Console
from diffusers import HunyuanVideoPipeline
from diffusers.utils import export_to_video

console = Console()

PRESET_RESOLUTIONS = {
    "480p": (720, 480),
    "720p": (1280, 720),  # HunyuanVideo native
    "1080p": (1920, 1080)
}

def load_shot_from_yaml(storyboard_path: str, shot_id: str):
    """Load specific shot by ID from storyboard v2"""
    with open(storyboard_path, 'r') as f:
        data = yaml.safe_load(f)

    for scene in data.get('scenes', []):
        for shot in scene.get('shots', []):
            if shot.get('id') == shot_id:
                return shot

    raise ValueError(f"Shot {shot_id} not found in storyboard")

def render_shot(shot, width, height, fps, out_path):
    """Render using HunyuanVideo with memory optimizations for 49GB VRAM"""
    console.print(f"[bold cyan]Rendering {shot['id']} with HunyuanVideo[/bold cyan]")

    model_path = Path(__file__).parent / "models" / "hunyuanvideo"

    # Load pipeline with memory-efficient settings
    console.print(f"[yellow]Loading HunyuanVideo pipeline (this may take a moment)...[/yellow]")

    pipe = HunyuanVideoPipeline.from_pretrained(
        str(model_path),
        torch_dtype=torch.bfloat16,  # bfloat16 for better quality
        variant="fp8"  # Use FP8 variant if available for memory efficiency
    )

    # Enable memory optimizations for 49GB VRAM
    pipe.enable_model_cpu_offload()  # Offload inactive components to CPU
    pipe.vae.enable_tiling()  # Enable VAE tiling for memory efficiency

    # Generate video
    prompt = shot['prompt']
    console.print(f"[cyan]Prompt: {prompt[:100]}...[/cyan]")

    # Calculate duration-based frames (target 6 seconds)
    # HunyuanVideo produces 24fps native, so 6s = 145 frames
    duration_s = shot.get('duration_s', 6)
    num_frames = min(int(duration_s * 24) + 1, 145)  # Max 145 frames (~6s @ 24fps)

    console.print(f"[yellow]Generating {num_frames} frames @ 720p (24fps native)...[/yellow]")

    video = pipe(
        prompt=prompt,
        num_videos_per_prompt=1,
        num_inference_steps=50,  # High quality inference
        num_frames=num_frames,
        guidance_scale=6.0,
        height=720,  # HunyuanVideo native 720p
        width=1280,
    ).frames[0]

    # Export to video at desired FPS
    console.print(f"[green]Exporting to {out_path}...[/green]")
    export_to_video(video, str(out_path), fps=fps)

    console.print(f"[bold green]✓ {shot['id']} complete! ({out_path.stat().st_size // 1024}KB)[/bold green]")

def main():
    parser = argparse.ArgumentParser(description="Render with HunyuanVideo")
    parser.add_argument("--storyboard", required=True, help="Path to storyboard YAML")
    parser.add_argument("--shot-id", required=True, help="Shot ID to render (e.g., r001)")
    parser.add_argument("--outdir", required=True, help="Output directory")
    parser.add_argument("--preset", default="720p", choices=["480p", "720p", "1080p"],
                        help="Resolution preset (720p recommended for HunyuanVideo)")

    args = parser.parse_args()

    out_dir = Path(args.outdir)
    inter_dir = out_dir / "intermediate"
    inter_dir.mkdir(parents=True, exist_ok=True)

    width, height = PRESET_RESOLUTIONS[args.preset]
    fps = 24  # HunyuanVideo native 24fps for cinematic quality

    shot = load_shot_from_yaml(args.storyboard, args.shot_id)
    out_path = inter_dir / f"{args.shot_id}.mp4"

    render_shot(shot, width, height, fps, out_path)

    return 0

if __name__ == "__main__":
    exit(main())
