#!/usr/bin/env python3
"""
Single shot renderer for Storyboard V2
Renders one shot at a time for granular control
"""

import argparse
import os
from pathlib import Path
import yaml
import subprocess
from rich.console import Console

from utils import models as model_utils
from utils import video as video_utils

console = Console()

PRESET_RESOLUTIONS = {
    "hd": (1920, 1080),
    "1080p": (1920, 1080),
    "4k": (3840, 2160),
}

def load_shot_from_yaml(storyboard_path: str, shot_id: str):
    """Load a specific shot by ID from storyboard v2 yaml"""
    with open(storyboard_path, 'r') as f:
        data = yaml.safe_load(f)

    # V2 yaml structure: scenes -> shots -> id
    for scene in data.get('scenes', []):
        for shot in scene.get('shots', []):
            if shot.get('id') == shot_id:
                return shot

    raise ValueError(f"Shot {shot_id} not found in storyboard")

def render_t2v(shot, width, height, fps, out_path):
    """Text-to-video using SDXL"""
    console.print(f"[cyan]Generating still for {shot['id']} with SDXL[/cyan]")

    pipe = model_utils.get_t2i()
    image = pipe(
        prompt=shot['prompt'],
        num_inference_steps=30,
        guidance_scale=7.5,
        width=width,
        height=height
    ).images[0]

    # Apply Ken Burns effect and save directly
    duration = shot['duration_s']
    video_utils.kenburns_from_still(image, out_path, duration, fps, size=(width, height))

    # Add overlay text if present
    if shot.get('overlay_text'):
        video_utils.overlay_texts(out_path, shot['overlay_text'])
    console.print(f"[green]✓ {shot['id']} rendered to {out_path}[/green]")

def render_img2vid(shot, width, height, fps, out_path):
    """Image-to-video using SVD"""
    console.print(f"[cyan]Generating base frame for {shot['id']}[/cyan]")

    # Generate base frame with SDXL
    t2i_pipe = model_utils.get_t2i()
    base_frame = t2i_pipe(
        prompt=shot['prompt'],
        num_inference_steps=25,
        guidance_scale=7.5,
        width=width,
        height=height
    ).images[0]

    console.print(f"[cyan]Animating {shot['id']} with Stable Video Diffusion (40 frames)[/cyan]")

    # Animate with SVD
    img2vid_pipe = model_utils.get_img2vid()
    result = img2vid_pipe(
        image=base_frame,
        num_frames=40,
        num_inference_steps=25,
        decode_chunk_size=2,  # Reduced to prevent OOM
        motion_bucket_id=127,
        noise_aug_strength=0.02
    ).frames[0]

    # Convert PIL images to numpy array
    frames = np.array([np.array(frame) for frame in result])

    # Write video
    video_utils.write_video(frames, out_path, fps)

    # Add overlay text if present
    if shot.get('overlay_text'):
        video_utils.overlay_texts(out_path, shot['overlay_text'])
    console.print(f"[green]✓ {shot['id']} rendered to {out_path}[/green]")

def main():
    parser = argparse.ArgumentParser(description="Render single shot from storyboard v2")
    parser.add_argument("--storyboard", required=True, help="Path to storyboard yaml")
    parser.add_argument("--shot-id", required=True, help="Shot ID (e.g. r001, r002)")
    parser.add_argument("--outdir", required=True, help="Output directory")
    parser.add_argument("--preset", default="1080p", choices=["hd", "1080p", "4k"])

    args = parser.parse_args()

    # Setup
    out_dir = Path(args.outdir)
    inter_dir = out_dir / "intermediate"
    inter_dir.mkdir(parents=True, exist_ok=True)

    width, height = PRESET_RESOLUTIONS[args.preset]
    fps = 30

    # Load shot
    console.print(f"[bold]Loading shot {args.shot_id}[/bold]")
    shot = load_shot_from_yaml(args.storyboard, args.shot_id)

    # Output path
    out_path = inter_dir / f"{args.shot_id}.mp4"

    # Render based on method
    method = shot['method']

    if method == 't2v':
        render_t2v(shot, width, height, fps, out_path)
    elif method == 'img2vid':
        render_img2vid(shot, width, height, fps, out_path)
    elif method == 'raw':
        console.print(f"[yellow]Raw footage method not implemented yet[/yellow]")
    else:
        console.print(f"[red]Unknown method: {method}[/red]")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
