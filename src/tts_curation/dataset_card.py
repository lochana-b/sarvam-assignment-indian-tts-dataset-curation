from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Any


def render_dataset_card(rows: list[dict[str, Any]], repo_id: str) -> str:
    totals: dict[str, float] = defaultdict(float)
    counts: dict[str, int] = defaultdict(int)
    languages: dict[str, str] = {}
    sources = set()
    for row in rows:
        bucket = row.get("bucket", "unknown")
        totals[bucket] += float(row.get("duration_seconds") or 0)
        counts[bucket] += 1
        languages[row.get("language_code", "")] = row.get("language_name", "")
        sources.add(row.get("source_url", ""))

    table_lines = [
        "| Bucket | Samples | Minutes |",
        "| --- | ---: | ---: |",
    ]
    for bucket in sorted(totals):
        table_lines.append(f"| {bucket} | {counts[bucket]} | {totals[bucket] / 60:.2f} |")
    table_lines.append(f"| total | {sum(counts.values())} | {sum(totals.values()) / 60:.2f} |")

    language_lines = "\n".join(
        f"- `{code}`: {name}" for code, name in sorted(languages.items()) if code
    )
    source_count = len([s for s in sources if s])

    return f"""---
pretty_name: Indian TTS YouTube Curated 60 Minute Dataset
language:
- en
- hi
license: other
task_categories:
- text-to-speech
tags:
- text-to-speech
- indian-english
- hindi
- sarvam
- youtube
---

# {repo_id}

This dataset contains manually reviewed YouTube-sourced speech clips curated for a small TTS training assignment. It is designed as a quality-focused 60-minute dataset with roughly 30 minutes of Indian English and 30 minutes of Hindi.

## Languages

{language_lines}

## Duration

{chr(10).join(table_lines)}

## Dataset Fields

- `audio`: 16 kHz mono WAV clip
- `transcript`: manually reviewed transcript
- `language_code`, `language_name`, `bucket`
- `emotion`, `style`
- `source_url`, `source_id`, `segment_id`
- `start_seconds`, `end_seconds`, `duration_seconds`
- `speaker_id`, `diarization_speaker_count`
- `quality_notes`, `reviewer_status`

## Curation Process

1. Candidate YouTube source regions were listed in a manifest.
2. Segments were cut and normalized to 16 kHz mono WAV.
3. Sarvam Saaras v3 batch STT was used with diarization enabled.
4. Sarvam chat completion was used to draft emotion/style labels.
5. Every retained clip was manually listened to, corrected, and marked `keep`.

## Source And License Notes

The dataset keeps source URLs and timestamps for traceability. The final release used {source_count} YouTube source URL(s). Reuse rights depend on the selected source videos and should be checked before downstream redistribution or commercial use.

## Created

Generated on {date.today().isoformat()}.
"""

