from __future__ import annotations

import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Any

import requests

from .io import ensure_dir, read_jsonl, write_json, write_jsonl


EMOTION_VALUES = [
    "neutral",
    "happy",
    "sad",
    "excited",
    "angry",
    "serious",
    "calm",
    "concerned",
    "other",
]

STYLE_VALUES = [
    "conversational",
    "formal",
    "narration",
    "interview",
    "news",
    "devotional",
    "dramatic",
    "other",
]


def _api_key(value: str | None = None) -> str:
    key = value or os.environ.get("SARVAM_API_KEY")
    if not key:
        raise RuntimeError("Set SARVAM_API_KEY or pass --sarvam-api-key")
    return key


def run_batch_asr(
    segments_path: str | Path,
    output_path: str | Path,
    sarvam_output_dir: str | Path,
    sarvam_api_key: str | None = None,
    num_speakers: int | None = None,
) -> None:
    try:
        from sarvamai import SarvamAI
    except ImportError as exc:
        raise RuntimeError("Install the sarvamai package before running ASR") from exc

    rows = read_jsonl(segments_path)
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["language_code"]].append(row)

    client = SarvamAI(api_subscription_key=_api_key(sarvam_api_key))
    all_rows: list[dict[str, Any]] = []
    ensure_dir(sarvam_output_dir)

    for language_code, language_rows in grouped.items():
        language_dir = ensure_dir(Path(sarvam_output_dir) / language_code)
        audio_paths = [row["audio_path"] for row in language_rows]
        job_kwargs: dict[str, Any] = {
            "model": "saaras:v3",
            "mode": "transcribe",
            "language_code": language_code,
            "with_diarization": True,
        }
        if num_speakers is not None:
            job_kwargs["num_speakers"] = num_speakers

        job = client.speech_to_text_job.create_job(**job_kwargs)
        job.upload_files(file_paths=audio_paths)
        job.start()
        job.wait_until_complete()
        file_results = job.get_file_results()
        write_json(language_dir / "file_results.json", file_results)
        job.download_outputs(output_dir=str(language_dir))

        result_map = _load_downloaded_outputs(language_dir, file_results)
        for row in language_rows:
            audio_name = Path(row["audio_path"]).name
            result = result_map.get(audio_name, {})
            merged = {
                **row,
                "transcript": result.get("transcript", ""),
                "sarvam_language_code": result.get("language_code", language_code),
                "sarvam_request_id": result.get("request_id", ""),
                "sarvam_model": "saaras:v3",
                "diarized_transcript": result.get("diarized_transcript", {}),
                "diarization_speaker_count": _speaker_count(result),
                "sarvam_raw_output_file": result.get("_output_file", ""),
            }
            all_rows.append(merged)

    write_jsonl(output_path, all_rows)


def _load_downloaded_outputs(
    language_dir: Path, file_results: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    by_input: dict[str, dict[str, Any]] = {}
    details = file_results.get("job_details", [])
    if not details:
        details = file_results.get("successful", [])

    output_to_input: dict[str, str] = {}
    for item in details:
        inputs = item.get("inputs") or []
        outputs = item.get("outputs") or []
        input_name = item.get("file_name") or (inputs[0].get("file_name") if inputs else "")
        output_name = item.get("output_file_name") or (
            outputs[0].get("file_name") if outputs else ""
        )
        if input_name and output_name:
            output_to_input[output_name] = Path(input_name).name

    for output_file in language_dir.glob("*.json"):
        if output_file.name == "file_results.json":
            continue
        with output_file.open("r", encoding="utf-8") as f:
            payload = json.load(f)
        payload["_output_file"] = str(output_file)
        input_name = output_to_input.get(output_file.name)
        if input_name:
            by_input[input_name] = payload
        else:
            by_input[output_file.stem + ".wav"] = payload
    return by_input


def _speaker_count(result: dict[str, Any]) -> int:
    entries = (result.get("diarized_transcript") or {}).get("entries") or []
    return len({str(entry.get("speaker_id", "")) for entry in entries if entry.get("speaker_id")})


def tag_emotions_and_style(
    segments_path: str | Path,
    output_path: str | Path,
    sarvam_api_key: str | None = None,
    model: str = "sarvam-30b",
) -> None:
    rows = read_jsonl(segments_path)
    tagged = [tag_one(row, sarvam_api_key=sarvam_api_key, model=model) for row in rows]
    write_jsonl(output_path, tagged)


def tag_one(
    row: dict[str, Any],
    sarvam_api_key: str | None = None,
    model: str = "sarvam-30b",
) -> dict[str, Any]:
    transcript = row.get("transcript") or ""
    if not transcript.strip():
        return {
            **row,
            "emotion": row.get("emotion_hint") or "other",
            "style": row.get("style_hint") or "other",
            "tag_confidence": "low",
            "tag_notes": "No transcript available; used manifest hints.",
        }

    prompt = {
        "task": "Classify a short TTS training audio segment using only its transcript and metadata.",
        "allowed_emotions": EMOTION_VALUES,
        "allowed_styles": STYLE_VALUES,
        "language_code": row.get("language_code"),
        "manifest_emotion_hint": row.get("emotion_hint", ""),
        "manifest_style_hint": row.get("style_hint", ""),
        "transcript": transcript,
        "instructions": (
            "Return strict JSON with keys emotion, style, confidence, notes. "
            "Use neutral/conversational when the text does not strongly imply emotion."
        ),
    }
    response = requests.post(
        "https://api.sarvam.ai/v1/chat/completions",
        headers={
            "api-subscription-key": _api_key(sarvam_api_key),
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "temperature": 0.0,
            "messages": [
                {
                    "role": "user",
                    "content": json.dumps(prompt, ensure_ascii=False),
                }
            ],
        },
        timeout=60,
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    parsed = _parse_json_content(content)
    emotion = parsed.get("emotion", "other")
    style = parsed.get("style", "other")
    if emotion not in EMOTION_VALUES:
        emotion = "other"
    if style not in STYLE_VALUES:
        style = "other"
    return {
        **row,
        "emotion": emotion,
        "style": style,
        "tag_confidence": parsed.get("confidence", ""),
        "tag_notes": parsed.get("notes", ""),
        "tag_model": model,
    }


def _parse_json_content(content: str) -> dict[str, Any]:
    content = content.strip()
    if content.startswith("```"):
        content = content.strip("`")
        if content.startswith("json"):
            content = content[4:].strip()
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        start = content.find("{")
        end = content.rfind("}")
        if start >= 0 and end > start:
            return json.loads(content[start : end + 1])
    return {}

