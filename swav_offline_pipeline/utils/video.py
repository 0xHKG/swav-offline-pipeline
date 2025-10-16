from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
from typing import Iterable, Sequence, Tuple

import numpy as np
from PIL import Image

DEFAULT_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _as_path(pathlike) -> Path:
    return pathlike if isinstance(pathlike, Path) else Path(pathlike)


def kenburns_from_still(
    pil_img: Image.Image,
    out_path,
    duration: float,
    fps: int,
    size: Tuple[int, int] = (3840, 2160),
) -> None:
    """Create a gentle Ken Burns move from a still image using ffmpeg zoompan."""
    out_path = _as_path(out_path)
    _ensure_parent(out_path)

    width, height = size
    frames = max(int(round(duration * fps)), 1)

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        resized = pil_img.convert("RGB").resize((width, height), Image.BICUBIC)
        resized.save(tmp.name)
        tmp_path = tmp.name

    zoom_increment = 0.05 / max(frames, 1)
    zoom_filter = f"zoompan=z='1+{zoom_increment}*on':d={frames}:s={width}x{height}"
    cmd = [
        "ffmpeg",
        "-y",
        "-loop",
        "1",
        "-i",
        tmp_path,
        "-vf",
        f"{zoom_filter},fps={fps}",
        "-t",
        f"{duration:.3f}",
        "-c:v",
        "libx264",
        "-crf",
        "10",
        "-preset",
        "slow",
        "-pix_fmt",
        "yuv420p",
        str(out_path),
    ]
    subprocess.run(cmd, check=True)
    Path(tmp_path).unlink(missing_ok=True)


def _escape_drawtext(text: str) -> str:
    return text.replace("\\", r"\\\\").replace(":", r"\:").replace("'", r"\'")


def overlay_texts(in_path, lines: Sequence[str], font: str = DEFAULT_FONT) -> None:
    """Overlay centered multiline text with subtle shadow using ffmpeg drawtext."""
    in_path = _as_path(in_path)
    temp_out = in_path.with_suffix(".tmp.mp4")
    _ensure_parent(temp_out)

    line_height = 64
    filter_parts = []
    line_count = len(lines)
    for idx, line in enumerate(lines):
        y_expr = f"(h/2 - {line_height * (line_count - 1) / 2} + {idx}*{line_height})"
        filter_parts.append(
            f"drawtext=fontfile={font}:text='{_escape_drawtext(line)}':"
            f"fontcolor=white:fontsize={line_height}:x=(w-text_w)/2:"
            f"y={y_expr}:shadowcolor=0x000000AA:shadowx=2:shadowy=2"
        )
    filter_chain = ",".join(filter_parts)
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(in_path),
        "-vf",
        filter_chain,
        "-c:v",
        "libx264",
        "-crf",
        "10",
        "-preset",
        "slow",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "copy",
        str(temp_out),
    ]
    subprocess.run(cmd, check=True)
    temp_out.replace(in_path)


def write_video(frames: np.ndarray, out_path, fps: int) -> None:
    """Encode an array of uint8 frames (T, H, W, C) into an H.264 video."""
    if frames.ndim != 4:
        raise ValueError("Frames array must be 4D: (T, H, W, C)")
    if frames.dtype != np.uint8:
        raise ValueError("Frames array must be uint8.")

    out_path = _as_path(out_path)
    _ensure_parent(out_path)

    frame_count, height, width, channels = frames.shape
    if channels != 3:
        raise ValueError("Frames must have 3 channels (RGB).")

    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "rawvideo",
        "-vcodec",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "-s",
        f"{width}x{height}",
        "-r",
        str(fps),
        "-i",
        "-",
        "-c:v",
        "libx264",
        "-crf",
        "10",
        "-preset",
        "slow",
        "-pix_fmt",
        "yuv420p",
        str(out_path),
    ]
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    try:
        process.stdin.write(frames.tobytes())
        process.stdin.close()
        return_code = process.wait()
        if return_code != 0:
            raise subprocess.CalledProcessError(return_code, cmd)
    finally:
        if process.poll() is None:
            process.terminate()
