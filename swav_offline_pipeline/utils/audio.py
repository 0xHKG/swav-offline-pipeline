from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Dict, List

import numpy as np
import soundfile as sf
import torch
from TTS.api import TTS

MODEL_ROOT = Path(__file__).resolve().parents[1] / "models"

_TTS_INSTANCE: TTS | None = None


def _load_tts() -> TTS:
    global _TTS_INSTANCE
    if _TTS_INSTANCE is None:
        model_dir = MODEL_ROOT / "xtts-v2"
        if not model_dir.exists():
            raise FileNotFoundError(f"XTTS v2 model not found at {model_dir}. Run download_models.sh first.")
        use_gpu = torch.cuda.is_available()
        _TTS_INSTANCE = TTS(model_path=str(model_dir), progress_bar=False, gpu=use_gpu)
    return _TTS_INSTANCE


def _select_speaker(tts: TTS, voice: str) -> str:
    speakers = getattr(tts, "speakers", None) or []
    if voice in speakers:
        return voice
    fallback_order = [voice, "male-en-2", "male", "female", "female-en-5"]
    for candidate in fallback_order:
        if candidate in speakers:
            return candidate
    return speakers[0] if speakers else voice


def synthesize_voiceover(blocks: List[Dict], out_wav: Path | str, voice: str = "male") -> None:
    """Synthesize narration for each block and concatenate into a single WAV file."""
    out_wav = Path(out_wav)
    out_wav.parent.mkdir(parents=True, exist_ok=True)

    if not blocks:
        silence = np.zeros(int(0.5 * 24000), dtype=np.float32)
        sf.write(out_wav, silence, 24000)
        return

    tts = _load_tts()
    speaker = _select_speaker(tts, voice)
    sample_rate = getattr(tts.synthesizer, "output_sample_rate", 24000)

    gap = int(sample_rate * 0.25)
    segments: List[np.ndarray] = []

    for idx, block in enumerate(blocks):
        text = block["text"].strip()
        if not text:
            continue
        wav = tts.tts(text=text, speaker=speaker, language="en")
        audio = np.asarray(wav, dtype=np.float32)
        if idx:
            segments.append(np.zeros(gap, dtype=np.float32))
        segments.append(audio)

    if not segments:
        segments.append(np.zeros(int(0.5 * sample_rate), dtype=np.float32))

    full = np.concatenate(segments)
    sf.write(out_wav, full, sample_rate)


def make_music(tag: str, out_wav: Path | str, duration: float, sample_rate: int = 48000) -> None:
    """Placeholder music bed: currently generates silence for the requested duration."""
    out_wav = Path(out_wav)
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    samples = int(max(duration, 0.1) * sample_rate)
    silence = np.zeros(samples, dtype=np.float32)
    sf.write(out_wav, silence, sample_rate)


def mix_audio(
    video_in: str,
    vo_wav: str,
    music_wav: str,
    out_path: str,
    codec: str = "h264",
) -> None:
    """Combine video with voiceover and ducked music, applying loudness normalization."""
    out_file = Path(out_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    audio_codec = "aac" if codec == "h264" else "pcm_s24le"
    audio_bitrate = "224k" if codec == "h264" else None

    filter_complex = (
        "[1:a]loudnorm=I=-16:LRA=11:TP=-1.5:print_format=never[vo];"
        "[2:a]volume=0.35[music_pre];"
        "[music_pre][vo]sidechaincompress=threshold=-28:ratio=6:attack=50:release=300:makeup=6[music_ducked];"
        "[vo][music_ducked]amix=inputs=2:weights=1 1:normalize=0[mix];"
        "[mix]loudnorm=I=-16:LRA=11:TP=-1.5:print_format=never[out]"
    )

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        video_in,
        "-i",
        vo_wav,
        "-i",
        music_wav,
        "-filter_complex",
        filter_complex,
        "-map",
        "0:v",
        "-map",
        "[out]",
        "-c:v",
        "copy",
        "-c:a",
        audio_codec,
    ]
    if audio_bitrate:
        cmd.extend(["-b:a", audio_bitrate])
    cmd.append(str(out_file))
    subprocess.run(cmd, check=True)
