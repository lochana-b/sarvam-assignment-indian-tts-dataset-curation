from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from .io import ensure_dir


def download_audio(url: str, output_path: str | Path) -> Path:
    output_path = Path(output_path)
    ensure_dir(output_path.parent)
    temp_template = str(output_path.with_suffix(".%(ext)s"))
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "yt_dlp",
            "--no-playlist",
            "--extract-audio",
            "--audio-format",
            "wav",
            "--audio-quality",
            "0",
            "--output",
            temp_template,
            url,
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"yt-dlp failed for {url}\nstdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )
    if not output_path.exists():
        candidates = list(output_path.parent.glob(output_path.stem + ".*"))
        wavs = [p for p in candidates if p.suffix.lower() == ".wav"]
        if not wavs:
            raise RuntimeError(f"download succeeded but {output_path} was not created")
        wavs[0].rename(output_path)
    return output_path

