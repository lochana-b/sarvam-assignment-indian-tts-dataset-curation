from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any

from datasets import Audio, Dataset, Features, Value
from huggingface_hub import HfApi

from .dataset_card import render_dataset_card
from .io import read_jsonl


def publish_dataset(
    metadata_path: str | Path,
    repo_id: str,
    token: str | None = None,
    private: bool = False,
) -> None:
    token = token or os.environ.get("HF_TOKEN")
    if not token:
        raise RuntimeError("Set HF_TOKEN or pass --hf-token")

    rows = read_jsonl(metadata_path)
    if not rows:
        raise RuntimeError(f"No rows found in {metadata_path}")

    prepared: list[dict[str, Any]] = []
    for row in rows:
        prepared.append(
            {
                "audio": row["audio_path"],
                "transcript": row["transcript"],
                "language_code": row["language_code"],
                "language_name": row["language_name"],
                "bucket": row["bucket"],
                "emotion": row.get("emotion", ""),
                "style": row.get("style", ""),
                "source_url": row["source_url"],
                "source_id": row["source_id"],
                "segment_id": row["segment_id"],
                "start_seconds": float(row["start_seconds"]),
                "end_seconds": float(row["end_seconds"]),
                "duration_seconds": float(row["duration_seconds"]),
                "speaker_id": row.get("speaker_id", ""),
                "diarization_speaker_count": int(row.get("diarization_speaker_count") or 0),
                "quality_notes": row.get("quality_notes", ""),
                "reviewer_status": row.get("review_status", row.get("reviewer_status", "")),
            }
        )

    features = Features(
        {
            "audio": Audio(sampling_rate=16000),
            "transcript": Value("string"),
            "language_code": Value("string"),
            "language_name": Value("string"),
            "bucket": Value("string"),
            "emotion": Value("string"),
            "style": Value("string"),
            "source_url": Value("string"),
            "source_id": Value("string"),
            "segment_id": Value("string"),
            "start_seconds": Value("float32"),
            "end_seconds": Value("float32"),
            "duration_seconds": Value("float32"),
            "speaker_id": Value("string"),
            "diarization_speaker_count": Value("int32"),
            "quality_notes": Value("string"),
            "reviewer_status": Value("string"),
        }
    )
    dataset = Dataset.from_list(prepared, features=features)
    api = HfApi(token=token)
    api.create_repo(repo_id, repo_type="dataset", private=private, exist_ok=True)
    dataset.push_to_hub(repo_id, token=token, private=private)
    card = render_dataset_card(rows, repo_id)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".md") as f:
        f.write(card)
        f.flush()
        api.upload_file(
            path_or_fileobj=f.name,
            path_in_repo="README.md",
            repo_id=repo_id,
            repo_type="dataset",
            token=token,
        )
