from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SegmentSpec:
    id: str
    start: float
    end: float
    emotion_hint: str = ""
    style_hint: str = ""
    notes: str = ""

    @property
    def duration(self) -> float:
        return max(0.0, self.end - self.start)


@dataclass(frozen=True)
class SourceSpec:
    id: str
    url: str
    bucket: str
    language_code: str
    language_name: str
    expected_speaker: str = ""
    license_note: str = ""
    source_notes: str = ""
    candidate_segments: list[SegmentSpec] = field(default_factory=list)


@dataclass(frozen=True)
class DatasetConfig:
    dataset: dict[str, Any]
    quality: dict[str, Any]
    sources: list[SourceSpec]


def parse_time(value: str | int | float) -> float:
    if isinstance(value, (int, float)):
        return float(value)

    value = value.strip()
    if not value:
        raise ValueError("empty timestamp")

    parts = value.split(":")
    if len(parts) == 1:
        return float(parts[0])
    if len(parts) == 2:
        minutes, seconds = parts
        return int(minutes) * 60 + float(seconds)
    if len(parts) == 3:
        hours, minutes, seconds = parts
        return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    raise ValueError(f"unsupported timestamp: {value!r}")


def load_config(path: str | Path) -> DatasetConfig:
    import yaml

    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    sources: list[SourceSpec] = []
    for source in raw.get("sources", []):
        segments = [
            SegmentSpec(
                id=str(item["id"]),
                start=parse_time(item["start"]),
                end=parse_time(item["end"]),
                emotion_hint=str(item.get("emotion_hint", "")),
                style_hint=str(item.get("style_hint", "")),
                notes=str(item.get("notes", "")),
            )
            for item in source.get("candidate_segments", [])
        ]
        sources.append(
            SourceSpec(
                id=str(source["id"]),
                url=str(source["url"]),
                bucket=str(source["bucket"]),
                language_code=str(source["language_code"]),
                language_name=str(source["language_name"]),
                expected_speaker=str(source.get("expected_speaker", "")),
                license_note=str(source.get("license_note", "")),
                source_notes=str(source.get("source_notes", "")),
                candidate_segments=segments,
            )
        )

    return DatasetConfig(
        dataset=raw.get("dataset", {}),
        quality=raw.get("quality", {}),
        sources=sources,
    )
