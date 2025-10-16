from __future__ import annotations

from pathlib import Path
from typing import List, Sequence

MIN_DURATION = 3.5
MAX_DURATION = 7.0
GAP = 0.25


def _format_timestamp(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    hours, ms = divmod(ms, 3_600_000)
    minutes, ms = divmod(ms, 60_000)
    secs, ms = divmod(ms, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{ms:03}"


def write_srt(blocks: Sequence[dict], out_path: Path | str) -> None:
    """Create an SRT file with adaptive timings and 250ms gaps between entries."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    entries: List[str] = []
    previous_end = 0.0

    for idx, block in enumerate(blocks, start=1):
        start = max(block.get("start", 0.0), previous_end)
        base_duration = float(block.get("duration", MIN_DURATION))
        desired = max(MIN_DURATION, min(MAX_DURATION, base_duration))
        end = start + desired
        hard_end = block.get("start", start) + base_duration
        if end > hard_end:
            end = hard_end
        if end - start < 0.75:
            end = start + 0.75
        text = block.get("text", "").strip()
        if not text:
            continue
        entries.append(
            "\n".join(
                [
                    str(idx),
                    f"{_format_timestamp(start)} --> {_format_timestamp(end)}",
                    text,
                    "",
                ]
            )
        )
        previous_end = end + GAP

    out_path.write_text("\n".join(entries), encoding="utf-8")
