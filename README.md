# Indian TTS Dataset Curation Pipeline

This repo builds a public Hugging Face dataset for the assignment:

- 60 minutes total clean single-speaker speech
- Around 30 minutes Indian English
- Around 30 minutes Hindi
- YouTube-sourced audio
- Accurate transcripts
- Emotion/style tags
- Sarvam APIs for ASR, diarization, and LLM tagging

The pipeline is intentionally manifest-driven so the important work stays visible: choosing good sources, listening, rejecting weak clips, correcting transcripts, and documenting the decisions.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

You also need `ffmpeg` and `ffprobe` on your PATH.

Set credentials:

```bash
export SARVAM_API_KEY="sk_..."
export HF_TOKEN="hf_..."
```

## Workflow

1. Copy the example manifest and add YouTube URLs plus candidate timestamps:

```bash
cp config/sources.example.yaml config/sources.yaml
```

2. Download source audio:

```bash
tts-curate download --manifest config/sources.yaml
```

3. Cut and normalize candidate segments:

```bash
tts-curate cut --manifest config/sources.yaml
```

4. Run Sarvam batch ASR with diarization:

```bash
tts-curate asr --segments metadata/segments_draft.jsonl
```

5. Add Sarvam LLM emotion/style tags:

```bash
tts-curate tag --segments metadata/asr_results.jsonl
```

6. Build a listening review sheet:

```bash
tts-curate review-sheet --segments metadata/tagged_segments.jsonl
```

Open `metadata/manual_review.csv`, listen to every clip, fix transcripts, and mark `review_status` as `keep` or `reject`.

7. Finalize reviewed metadata:

```bash
tts-curate finalize \
  --segments metadata/tagged_segments.jsonl \
  --review metadata/manual_review.csv
```

8. Inspect totals:

```bash
tts-curate stats --metadata metadata/final_metadata.jsonl
```

9. Publish to Hugging Face:

```bash
tts-curate publish \
  --metadata metadata/final_metadata.jsonl \
  --repo-id YOUR_HF_USERNAME/indian-tts-youtube-curated-60min
```

10. Build the report PDF:

```bash
cp report/report_template.md report/report.md
tts-curate build-report --input report/report.md --output report/report.pdf
```

## Data Quality Rubric

Keep a clip only if:

- It is a single dominant speaker.
- No music, applause, crowd speech, or background speech competes with the voice.
- The voice is natural, not synthetic or heavily processed.
- The transcript is manually corrected and matches the audio.
- Segment boundaries do not cut words.
- Volume is stable and non-clipped.
- Speaker identity, source URL, start/end timestamps, language, and tags are recorded.

Prefer 30-60 second clips. Shorter clips are okay when the speech is excellent, but avoid many tiny clips because they make review and model training noisier.

## Dataset Schema

The Hugging Face dataset contains:

- `audio`: WAV audio file
- `transcript`: manually reviewed transcript
- `language_code`: e.g. `en-IN`, `hi-IN`
- `language_name`: e.g. `Indian English`, `Hindi`
- `bucket`: `indian_english` or `hindi`
- `emotion`: one of `neutral`, `happy`, `sad`, `excited`, `angry`, `serious`, `calm`, `concerned`, `other`
- `style`: one of `conversational`, `formal`, `narration`, `interview`, `news`, `devotional`, `dramatic`, `other`
- `source_url`
- `source_id`
- `segment_id`
- `start_seconds`
- `end_seconds`
- `duration_seconds`
- `speaker_id`
- `diarization_speaker_count`
- `quality_notes`
- `reviewer_status`

## Important Notes

Do not commit downloaded YouTube audio or generated segments to GitHub. Publish the curated final dataset to Hugging Face only when you have verified that your source choices and reuse are acceptable for the assignment.

Prefer YouTube videos with clear reuse terms, official channels, or explicit permission. Keep license/source notes in the manifest and dataset card.

