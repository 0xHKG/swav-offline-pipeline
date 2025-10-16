#!/usr/bin/env python3
"""
Offline orchestration pipeline for Swavlamban 2025.

Reads storyboard YAML, generates visual assets, synthesizes audio, and produces
final masters with captions. All generation is local; no network calls are made
after models are downloaded.
"""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import subprocess

import yaml
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from utils import audio as audio_utils
from utils import models as model_utils
from utils import subtitles as subtitle_utils
from utils import video as video_utils

console = Console()


@dataclass
class ShotSpec:
    row_no: int
    method: str
    prompt: str
    duration_s: float
    narration: str
    overlay_text: List[str] | None = None
    source_path: str | None = None  # used for raw footage


@dataclass
class RenderedShot:
    spec: ShotSpec
    video_path: Path


PRESET_RESOLUTIONS: Dict[str, Tuple[int, int]] = {
    "hd": (1920, 1080),
    "4k": (3840, 2160),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Swavlamban 2025 offline render orchestrator")
    parser.add_argument("--storyboard", required=True, type=Path, help="Path to storyboard YAML")
    parser.add_argument("--outdir", required=True, type=Path, help="Output directory for renders")
    parser.add_argument("--gpus", default="0", help="Comma-separated GPU indices to expose (CUDA_VISIBLE_DEVICES)")
    parser.add_argument("--preset", choices=PRESET_RESOLUTIONS.keys(), default="4k", help="Output resolution preset")
    parser.add_argument("--master", choices=("h264", "prores"), default="h264", help="Final master codec")
    return parser.parse_args()


def load_storyboard(path: Path) -> Dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if "project" not in data or "scenes" not in data:
        raise ValueError("Storyboard must contain 'project' and 'scenes' keys.")
    return data


def ensure_env(args: argparse.Namespace, outdir: Path) -> Tuple[int, int]:
    os.environ["CUDA_VISIBLE_DEVICES"] = args.gpus
    width, height = PRESET_RESOLUTIONS[args.preset]
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "intermediate").mkdir(parents=True, exist_ok=True)
    return width, height


def render_t2v(shot: ShotSpec, width: int, height: int, fps: int, out_path: Path) -> None:
    pipe = model_utils.get_t2i()
    console.log(f"Generating still for row {shot.row_no} with SDXL")
    image = pipe(
        prompt=shot.prompt,
        height=height,
        width=width,
        guidance_scale=7.0,
        num_inference_steps=30,
        output_type="pil",
    ).images[0]
    video_utils.kenburns_from_still(image, out_path, shot.duration_s, fps, size=(width, height))


def _safe_frame_dimensions(width: int, height: int) -> Tuple[int, int]:
    safe_w = (width // 64) * 64
    safe_h = (height // 64) * 64
    return max(64, safe_w), max(64, safe_h)


def render_img2vid(shot: ShotSpec, width: int, height: int, fps: int, out_path: Path) -> None:
    safe_w, safe_h = _safe_frame_dimensions(width, height)
    base_pipe = model_utils.get_t2i()
    console.log(f"Generating base frame for row {shot.row_no}")
    base_image = base_pipe(
        prompt=shot.prompt,
        height=safe_h,
        width=safe_w,
        guidance_scale=6.5,
        num_inference_steps=25,
        output_type="pil",
    ).images[0]

    img2vid_pipe = model_utils.get_img2vid()
    target_frames = max(int(round(shot.duration_s * fps)), 1)
    request_frames = min(target_frames, 40)

    console.log(f"Animating row {shot.row_no} with Stable Video Diffusion ({request_frames} frames)")
    result = img2vid_pipe(
        image=base_image,
        num_frames=request_frames,
        min_guidance_scale=1.0,
        max_guidance_scale=3.0,
        motion_bucket_id=127,
        noise_aug_strength=0.1,
    )
    frames = result.frames  # shape (batch, frames, channels, height, width)
    if isinstance(frames, list):
        frames = frames[0]
    if hasattr(frames, "cpu"):
        frames = frames.cpu().numpy()
    if frames.shape[0] != request_frames:
        frames = frames[:request_frames]
    import numpy as np

    frames = (frames * 255.0).clip(0, 255).astype("uint8").transpose(0, 2, 3, 1)
    if frames.shape[0] != target_frames:
        idx = np.linspace(0, frames.shape[0] - 1, target_frames).round().astype(int)
        frames = frames[idx]
    if (frames.shape[2], frames.shape[1]) != (width, height):
        from PIL import Image

        resized = []
        for frame in frames:
            resized.append(Image.fromarray(frame).resize((width, height), Image.BICUBIC))
        frames = np.stack([np.array(f) for f in resized], axis=0)
    video_utils.write_video(frames, out_path, fps)


def render_raw(shot: ShotSpec, width: int, height: int, fps: int, out_path: Path) -> None:
    if not shot.source_path:
        raise ValueError(f"Shot {shot.row_no} is marked as raw but no source_path provided.")
    src = Path(shot.source_path)
    if not src.exists():
        raise FileNotFoundError(f"Raw media for shot {shot.row_no} not found: {src}")
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(src),
            "-vf",
            f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2",
            "-r",
            str(fps),
            "-c:v",
            "libx264",
            "-crf",
            "10",
            "-pix_fmt",
            "yuv420p",
            str(out_path),
        ],
        check=True,
    )


def concat_videos(paths: Iterable[Path], out_path: Path) -> None:
    concat_file = out_path.with_suffix(".txt")
    concat_file.write_text("".join(f"file '{p.as_posix()}'\n" for p in paths), encoding="utf-8")
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_file),
            "-c",
            "copy",
            str(out_path),
        ],
        check=True,
    )
    concat_file.unlink(missing_ok=True)


def build_voice_blocks(shots: List[RenderedShot]) -> List[Dict]:
    blocks: List[Dict] = []
    timeline = 0.0
    for shot in shots:
        blocks.append(
            {
                "row_no": shot.spec.row_no,
                "text": shot.spec.narration,
                "duration": shot.spec.duration_s,
                "start": timeline,
            }
        )
        timeline += shot.spec.duration_s
    return blocks


def determine_master_path(outdir: Path, master: str) -> Path:
    if master == "h264":
        return outdir / "final_swavlamban.mp4"
    return outdir / "final_swavlamban.mov"


def mux_audio(master_codec: str, video_path: Path, vo_wav: Path, music_wav: Path, out_path: Path) -> None:
    audio_utils.mix_audio(str(video_path), str(vo_wav), str(music_wav), str(out_path), codec=master_codec)


def main() -> None:
    args = parse_args()
    storyboard = load_storyboard(args.storyboard)
    fps = storyboard["project"].get("fps", 30)
    voice_choice = storyboard["project"].get("voice", "male")
    music_tag = storyboard["project"].get("music_tag", "")

    width, height = ensure_env(args, args.outdir)
    intermediate_dir = args.outdir / "intermediate"

    console.rule("[bold blue]Swavlamban 2025 Offline Render")

    rendered: List[RenderedShot] = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Rendering storyboard", total=None)
        for scene in storyboard["scenes"]:
            scene_name = scene.get("name", "Unnamed Scene")
            console.log(f"[green]Scene: {scene_name}")
            for shot_dict in scene["shots"]:
                spec = ShotSpec(
                    row_no=int(shot_dict["row_no"]),
                    method=shot_dict["method"],
                    prompt=shot_dict["prompt"],
                    duration_s=float(shot_dict["duration_s"]),
                    narration=shot_dict["narration"],
                    overlay_text=shot_dict.get("overlay_text"),
                    source_path=shot_dict.get("path"),
                )
                out_path = intermediate_dir / f"shot_{spec.row_no:03d}.mp4"

                if spec.method == "t2v":
                    render_t2v(spec, width, height, fps, out_path)
                elif spec.method == "img2vid":
                    render_img2vid(spec, width, height, fps, out_path)
                elif spec.method == "raw":
                    render_raw(spec, width, height, fps, out_path)
                else:
                    raise ValueError(f"Unsupported method '{spec.method}' in row {spec.row_no}")

                if spec.overlay_text:
                    video_utils.overlay_texts(out_path, spec.overlay_text)

                rendered.append(RenderedShot(spec=spec, video_path=out_path))
                progress.advance(task)

    concat_path = intermediate_dir / "timeline_no_audio.mp4"
    concat_videos([shot.video_path for shot in rendered], concat_path)

    voice_blocks = build_voice_blocks(rendered)
    vo_wav = intermediate_dir / "voiceover.wav"
    console.log("Synthesizing voiceover...")
    audio_utils.synthesize_voiceover(voice_blocks, vo_wav, voice=voice_choice)

    music_wav = intermediate_dir / "music.wav"
    total_duration = sum(block["duration"] for block in voice_blocks)
    console.log("Preparing music bed (silence placeholder)...")
    audio_utils.make_music(music_tag, music_wav, total_duration)

    final_path = determine_master_path(args.outdir, args.master)
    console.log(f"Mixing final audio and muxing into {final_path.name}...")
    mux_audio(args.master, concat_path, vo_wav, music_wav, final_path)

    subtitles_path = args.outdir / "captions.srt"
    console.log("Writing captions...")
    subtitle_utils.write_srt(voice_blocks, subtitles_path)

    console.rule("[bold green]Render complete")
    console.print(f"Final master: {final_path}")
    console.print(f"Captions: {subtitles_path}")


if __name__ == "__main__":
    main()
