# Manual Review Rubric

Use this rubric for every candidate clip before it enters the final dataset.

## Keep

- Single speaker throughout the clip.
- Transcript is corrected by listening, not accepted blindly from ASR.
- No clipped words at the beginning or end.
- No background music, crowd noise, applause, overlapping speech, or loud reverb.
- Natural speech with enough prosody for TTS training.
- Emotion/style tags are reasonable and not over-specific.
- Duration is usually 30-60 seconds.

## Reject

- Multiple speakers or interviewer overlap.
- Intro/outro music, applause, laughter over speech, or background TV/radio.
- Whispery, far-field, heavily compressed, or reverberant audio.
- Segment starts/ends mid-word.
- Transcript is uncertain after manual review.
- Strong code-switching that makes the selected language label misleading.
- Copyright/license uncertainty that makes public redistribution risky.

## Review Labels

- `keep`: ready for final dataset.
- `reject`: do not publish.
- `needs_edit`: good audio, but timestamp/transcript/tag needs correction.

