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

def enhance_prompt(original_prompt, shot_id):
    """Enhance prompts for better HunyuanVideo output quality

    Adds cinematic keywords, style descriptors, and quality boosters.
    Removes text overlays (AI can't generate readable text).
    """
    # Remove text overlay instructions (Super:, overlay text, quotes)
    import re
    prompt = re.sub(r'Super:\s*["\'].*?["\']', '', original_prompt)
    prompt = re.sub(r'["\'].*?["\']', '', prompt)

    # Remove editing/audio cues
    editing_terms = ['Black to', 'fade to', 'cut to', 'swell', 'dissolve', 'transition']
    for term in editing_terms:
        prompt = prompt.replace(term, '')

    # Clean up extra whitespace/punctuation
    prompt = re.sub(r'\s+', ' ', prompt).strip()
    prompt = re.sub(r'[;,]\s*$', '', prompt)

    # Quality and style boosters
    quality = "photorealistic 4K footage, sharp focus, high detail, professional cinematography"

    # Style based on content
    prompt_lower = prompt.lower()
    if any(term in prompt_lower for term in ['naval', 'ship', 'submarine', 'carrier', 'destroyer']):
        style = "cinematic naval documentary style, dramatic ocean lighting"
        camera = "stable wide shot"
    elif any(term in prompt_lower for term in ['exhibition', 'hall', 'desk', 'corridor']):
        style = "professional corporate event videography, clean modern interior"
        camera = "smooth tracking shot" if 'walk' in prompt_lower else "static medium shot"
    elif any(term in prompt_lower for term in ['officer', 'sailor', 'crew', 'team']):
        style = "respectful military documentary style, dignified presentation"
        camera = "steady handheld"
    else:
        style = "cinematic documentary style, professional composition"
        camera = "static establishing shot"

    # Combine (only if not already present)
    enhanced = f"{prompt}, {camera}, {style}, {quality}"

    return enhanced

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

    # Enhance prompt for better quality
    original_prompt = shot['prompt']
    prompt = enhance_prompt(original_prompt, shot['id'])

    console.print(f"[dim]Original: {original_prompt[:80]}...[/dim]")
    console.print(f"[cyan]Enhanced: {prompt[:100]}...[/cyan]")

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
