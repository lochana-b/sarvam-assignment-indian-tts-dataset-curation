# Indian TTS Dataset Curation Report

Candidate: YOUR NAME  
Deadline: Sunday, 7 June 2026, 11:59 PM IST

## Dataset Links

- Hugging Face dataset: TODO
- GitHub repository: TODO

## Summary

I built a 60-minute TTS training dataset from YouTube-sourced clean single-speaker speech:

| Bucket | Language | Target | Final duration | Samples |
| --- | --- | ---: | ---: | ---: |
| Indian English | en-IN | 30 min | TODO | TODO |
| Hindi | hi-IN | 30 min | TODO | TODO |
| Total | Mixed | 60 min | TODO | TODO |

## Pipeline

The pipeline is manifest-driven:

1. I listed candidate YouTube sources and timestamps in `config/sources.yaml`.
2. `tts-curate download` downloaded source audio locally.
3. `tts-curate cut` extracted candidate segments, converted them to 16 kHz mono WAV, and applied light loudness normalization.
4. `tts-curate asr` used Sarvam Saaras v3 batch STT with diarization enabled.
5. `tts-curate tag` used a Sarvam chat model to label emotion and style.
6. `tts-curate review-sheet` generated a CSV for manual listening review.
7. I manually listened, corrected transcripts, rejected bad clips, and marked approved clips as `keep`.
8. `tts-curate finalize` created final metadata.
9. `tts-curate publish` pushed the reviewed dataset to Hugging Face.

## Source Selection

Describe the channels/videos you used, why you selected them, and how you checked that each had a clean single-speaker region.

| Source | Language | Reason chosen | Rejected portions |
| --- | --- | --- | --- |
| TODO | TODO | TODO | TODO |

## Iterations

Document concrete improvements you made. Examples:

| Iteration | Problem found | Change made | Result |
| --- | --- | --- | --- |
| 1 | Intro music was present in early clips | Moved start timestamps past intros | Cleaner speech-only clips |
| 2 | Diarization showed two speakers in interview answers | Kept monologue stretches only | Better single-speaker consistency |
| 3 | ASR normalized some spoken numbers incorrectly | Manually corrected transcripts | More faithful TTS text |

## Quality Decisions

Summarize your judgment calls:

- Minimum acceptable audio quality:
- How you handled code-switching:
- How you decided emotion/style tags:
- How you handled unclear words:
- How you treated license/source risk:

## What Worked

TODO

## What Did Not Work

TODO

## Observations

TODO: mention ASR strengths/weaknesses by language, diarization reliability, common rejection causes, and transcript correction patterns.

## Improvements With More Time

TODO: mention more speakers, stricter licensing pass, phonetic balance, better noise metrics, second-pass human review, train/dev/test split, and richer prosody labels.

