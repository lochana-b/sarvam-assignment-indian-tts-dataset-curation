from __future__ import annotations

import json
import math
import shutil
import subprocess
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf

from .io import ensure_dir


def require_tool(name: str) -> None:
    if shutil.which(name) is None:
        raise RuntimeError(f"{name} is required but was not found on PATH")


def run_checked(args: list[str]) -> None:
    completed = subprocess.run(args, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(
            f"Command failed: {' '.join(args)}\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )


def probe_duration(path: str | Path) -> float:
    require_tool("ffprobe")
    completed = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            str(path),
        ],
        text=True,
        capture_output=True,
        check=True,
    )
    payload = json.loads(completed.stdout)
    return float(payload["format"]["duration"])


def cut_normalized_segment(
    source_audio: str | Path,
    output_audio: str | Path,
    start_seconds: float,
    end_seconds: float,
    sample_rate: int = 16000,
) -> None:
    require_tool("ffmpeg")
    output_audio = Path(output_audio)
    ensure_dir(output_audio.parent)
    duration = end_seconds - start_seconds
    if duration <= 0:
        raise ValueError(f"invalid segment duration: {duration}")

    run_checked(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-ss",
            f"{start_seconds:.3f}",
            "-t",
            f"{duration:.3f}",
            "-i",
            str(source_audio),
            "-vn",
            "-ac",
            "1",
            "-ar",
            str(sample_rate),
            "-af",
            "highpass=f=70,lowpass=f=7600,loudnorm=I=-23:TP=-2:LRA=11",
            str(output_audio),
        ]
    )


def analyze_audio(path: str | Path) -> dict[str, Any]:
    data, sample_rate = sf.read(path, always_2d=False)
    if data.ndim > 1:
        data = data.mean(axis=1)
    data = data.astype(np.float64)
    duration = len(data) / float(sample_rate)
    abs_data = np.abs(data)
    peak = float(abs_data.max()) if len(abs_data) else 0.0
    rms = float(math.sqrt(np.mean(np.square(data)))) if len(data) else 0.0
    silence_ratio = float(np.mean(abs_data < 0.001)) if len(abs_data) else 1.0
    clipped_ratio = float(np.mean(abs_data >= 0.999)) if len(abs_data) else 0.0

    return {
        "sample_rate": sample_rate,
        "duration_seconds": round(duration, 3),
        "peak_dbfs": round(20 * math.log10(max(peak, 1e-12)), 2),
        "rms_dbfs": round(20 * math.log10(max(rms, 1e-12)), 2),
        "silence_ratio": round(silence_ratio, 4),
        "clipped_ratio": round(clipped_ratio, 6),
    }

