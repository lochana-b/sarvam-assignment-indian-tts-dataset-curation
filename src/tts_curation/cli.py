from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

import pandas as pd
from rich.console import Console
from rich.table import Table

from .audio import analyze_audio, cut_normalized_segment
from .config import load_config
from .hf_publish import publish_dataset
from .io import ensure_dir, read_jsonl, write_jsonl
from .reporting import markdown_to_pdf
from .sarvam import run_batch_asr, tag_emotions_and_style
from .youtube import download_audio

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(prog="tts-curate")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("download", help="Download YouTube source audio listed in the manifest.")
    p.add_argument("--manifest", default="config/sources.yaml")
    p.add_argument("--raw-dir", default="data/raw")
    p.set_defaults(func=cmd_download)

    p = sub.add_parser("cut", help="Cut candidate segments and normalize audio.")
    p.add_argument("--manifest", default="config/sources.yaml")
    p.add_argument("--raw-dir", default="data/raw")
    p.add_argument("--segments-dir", default="data/segments")
    p.add_argument("--output", default="metadata/segments_draft.jsonl")
    p.set_defaults(func=cmd_cut)

    p = sub.add_parser("asr", help="Run Sarvam batch ASR and diarization.")
    p.add_argument("--segments", default="metadata/segments_draft.jsonl")
    p.add_argument("--output", default="metadata/asr_results.jsonl")
    p.add_argument("--sarvam-output-dir", default="metadata/sarvam")
    p.add_argument("--sarvam-api-key", default=None)
    p.add_argument("--num-speakers", type=int, default=None)
    p.set_defaults(func=cmd_asr)

    p = sub.add_parser("tag", help="Use Sarvam LLM to assign emotion/style tags.")
    p.add_argument("--segments", default="metadata/asr_results.jsonl")
    p.add_argument("--output", default="metadata/tagged_segments.jsonl")
    p.add_argument("--sarvam-api-key", default=None)
    p.add_argument("--model", default="sarvam-30b")
    p.set_defaults(func=cmd_tag)

    p = sub.add_parser("review-sheet", help="Create a CSV for manual listening review.")
    p.add_argument("--segments", default="metadata/tagged_segments.jsonl")
    p.add_argument("--output", default="metadata/manual_review.csv")
    p.set_defaults(func=cmd_review_sheet)

    p = sub.add_parser("finalize", help="Merge manual review edits and keep approved rows.")
    p.add_argument("--segments", default="metadata/tagged_segments.jsonl")
    p.add_argument("--review", default="metadata/manual_review.csv")
    p.add_argument("--output", default="metadata/final_metadata.jsonl")
    p.set_defaults(func=cmd_finalize)

    p = sub.add_parser("stats", help="Print duration totals by language bucket.")
    p.add_argument("--metadata", default="metadata/final_metadata.jsonl")
    p.set_defaults(func=cmd_stats)

    p = sub.add_parser("publish", help="Publish the final dataset to Hugging Face.")
    p.add_argument("--metadata", default="metadata/final_metadata.jsonl")
    p.add_argument("--repo-id", required=True)
    p.add_argument("--hf-token", default=None)
    p.add_argument("--private", action="store_true")
    p.set_defaults(func=cmd_publish)

    p = sub.add_parser("build-report", help="Render a Markdown report to PDF.")
    p.add_argument("--input", default="report/report.md")
    p.add_argument("--output", default="report/report.pdf")
    p.set_defaults(func=cmd_build_report)

    args = parser.parse_args()
    args.func(args)


def cmd_download(args: argparse.Namespace) -> None:
    cfg = load_config(args.manifest)
    raw_dir = ensure_dir(args.raw_dir)
    for source in cfg.sources:
        out = raw_dir / f"{source.id}.wav"
        if out.exists():
            console.print(f"[green]exists[/green] {out}")
            continue
        console.print(f"[cyan]download[/cyan] {source.id}")
        download_audio(source.url, out)


def cmd_cut(args: argparse.Namespace) -> None:
    cfg = load_config(args.manifest)
    raw_dir = Path(args.raw_dir)
    segments_dir = ensure_dir(args.segments_dir)
    sample_rate = int(cfg.quality.get("target_sample_rate", 16000))
    rows = []

    for source in cfg.sources:
        source_audio = raw_dir / f"{source.id}.wav"
        if not source_audio.exists():
            raise RuntimeError(f"Missing source audio: {source_audio}. Run download first.")
        for segment in source.candidate_segments:
            audio_path = segments_dir / source.bucket / f"{segment.id}.wav"
            cut_normalized_segment(
                source_audio,
                audio_path,
                segment.start,
                segment.end,
                sample_rate=sample_rate,
            )
            analysis = analyze_audio(audio_path)
            rows.append(
                {
                    "source_id": source.id,
                    "source_url": source.url,
                    "bucket": source.bucket,
                    "language_code": source.language_code,
                    "language_name": source.language_name,
                    "segment_id": segment.id,
                    "audio_path": str(audio_path),
                    "start_seconds": round(segment.start, 3),
                    "end_seconds": round(segment.end, 3),
                    "duration_seconds": analysis["duration_seconds"],
                    "expected_speaker": source.expected_speaker,
                    "speaker_id": "",
                    "emotion_hint": segment.emotion_hint,
                    "style_hint": segment.style_hint,
                    "license_note": source.license_note,
                    "source_notes": source.source_notes,
                    "quality_notes": segment.notes,
                    **analysis,
                }
            )
    write_jsonl(args.output, rows)
    console.print(f"[green]wrote[/green] {args.output} ({len(rows)} rows)")


def cmd_asr(args: argparse.Namespace) -> None:
    run_batch_asr(
        args.segments,
        args.output,
        args.sarvam_output_dir,
        sarvam_api_key=args.sarvam_api_key,
        num_speakers=args.num_speakers,
    )
    console.print(f"[green]wrote[/green] {args.output}")


def cmd_tag(args: argparse.Namespace) -> None:
    tag_emotions_and_style(
        args.segments,
        args.output,
        sarvam_api_key=args.sarvam_api_key,
        model=args.model,
    )
    console.print(f"[green]wrote[/green] {args.output}")


def cmd_review_sheet(args: argparse.Namespace) -> None:
    rows = read_jsonl(args.segments)
    review_rows = []
    for row in rows:
        review_rows.append(
            {
                "segment_id": row["segment_id"],
                "audio_path": row["audio_path"],
                "bucket": row["bucket"],
                "language_code": row["language_code"],
                "duration_seconds": row["duration_seconds"],
                "transcript": row.get("transcript", ""),
                "corrected_transcript": row.get("transcript", ""),
                "emotion": row.get("emotion", row.get("emotion_hint", "")),
                "style": row.get("style", row.get("style_hint", "")),
                "speaker_id": row.get("speaker_id", row.get("expected_speaker", "")),
                "review_status": "needs_edit",
                "quality_notes": row.get("quality_notes", ""),
                "source_url": row["source_url"],
                "start_seconds": row["start_seconds"],
                "end_seconds": row["end_seconds"],
                "diarization_speaker_count": row.get("diarization_speaker_count", ""),
            }
        )
    ensure_dir(Path(args.output).parent)
    pd.DataFrame(review_rows).to_csv(args.output, index=False)
    console.print(f"[green]wrote[/green] {args.output}")


def cmd_finalize(args: argparse.Namespace) -> None:
    rows = {row["segment_id"]: row for row in read_jsonl(args.segments)}
    review = pd.read_csv(args.review).fillna("")
    final_rows = []

    for item in review.to_dict(orient="records"):
        if str(item.get("review_status", "")).strip().lower() != "keep":
            continue
        segment_id = str(item["segment_id"])
        if segment_id not in rows:
            raise RuntimeError(f"Review row references unknown segment: {segment_id}")
        row = dict(rows[segment_id])
        row["transcript"] = str(item.get("corrected_transcript") or item.get("transcript") or "")
        row["emotion"] = str(item.get("emotion") or row.get("emotion") or row.get("emotion_hint") or "")
        row["style"] = str(item.get("style") or row.get("style") or row.get("style_hint") or "")
        row["speaker_id"] = str(item.get("speaker_id") or row.get("speaker_id") or row.get("expected_speaker") or "")
        row["review_status"] = "keep"
        row["quality_notes"] = str(item.get("quality_notes") or row.get("quality_notes") or "")
        final_rows.append(row)

    write_jsonl(args.output, final_rows)
    console.print(f"[green]wrote[/green] {args.output} ({len(final_rows)} kept rows)")
    _print_stats(final_rows)


def cmd_stats(args: argparse.Namespace) -> None:
    rows = read_jsonl(args.metadata)
    _print_stats(rows)


def cmd_publish(args: argparse.Namespace) -> None:
    publish_dataset(args.metadata, args.repo_id, token=args.hf_token, private=args.private)
    console.print(f"[green]published[/green] https://huggingface.co/datasets/{args.repo_id}")


def cmd_build_report(args: argparse.Namespace) -> None:
    markdown_to_pdf(args.input, args.output)
    console.print(f"[green]wrote[/green] {args.output}")


def _print_stats(rows: list[dict]) -> None:
    totals: dict[str, float] = defaultdict(float)
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        bucket = row.get("bucket", "unknown")
        totals[bucket] += float(row.get("duration_seconds") or 0)
        counts[bucket] += 1

    table = Table(title="Dataset duration")
    table.add_column("Bucket")
    table.add_column("Samples", justify="right")
    table.add_column("Minutes", justify="right")
    for bucket in sorted(totals):
        table.add_row(bucket, str(counts[bucket]), f"{totals[bucket] / 60:.2f}")
    table.add_row("TOTAL", str(sum(counts.values())), f"{sum(totals.values()) / 60:.2f}")
    console.print(table)

