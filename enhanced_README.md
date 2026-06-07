---
language:
- en
- hi
license: cc-by-nc-4.0
size_categories:
- n<1K
task_categories:
- text-to-speech
pretty_name: Indian TTS YouTube Curated 60 Minute Dataset
tags:
- text-to-speech
- indian-english
- hindi
- sarvam
- youtube
- audio
- speech
dataset_info:
  features:
  - name: audio
    dtype: audio
  - name: transcript
    dtype: string
  - name: language_code
    dtype: string
  - name: language_name
    dtype: string
  - name: bucket
    dtype: string
  - name: emotion
    dtype: string
  - name: style
    dtype: string
  - name: source_url
    dtype: string
  - name: source_id
    dtype: string
  - name: segment_id
    dtype: string
  - name: start_seconds
    dtype: float32
  - name: end_seconds
    dtype: float32
  - name: duration_seconds
    dtype: float32
  - name: speaker_id
    dtype: string
  - name: diarization_speaker_count
    dtype: int32
  - name: quality_notes
    dtype: string
  - name: reviewer_status
    dtype: string
  splits:
  - name: train
    num_examples: 63
configs:
- config_name: default
  data_files:
  - split: train
    path: data/train-*
---

# Indian TTS YouTube Curated Dataset (60 Minutes)

## Dataset Summary

This dataset contains **63 manually curated audio segments** totaling approximately **60 minutes** of high-quality speech data for Text-to-Speech (TTS) training. The dataset is balanced between Indian English and Hindi, with careful attention to audio quality, transcript accuracy, and emotional/stylistic diversity.

### Key Statistics

| Language | Segments | Duration | Quality |
|----------|----------|----------|---------|
| **Indian English** | 32 | 30.17 min | Manually reviewed |
| **Hindi** | 31 | 29.48 min | Manually reviewed |
| **TOTAL** | **63** | **59.65 min** | ✅ Production ready |

### Dataset Highlights

- 🎯 **Single Speaker Segments**: All clips feature a single dominant speaker
- 📝 **Manual Transcript Correction**: 65% of transcripts manually corrected for accuracy
- 🎭 **Emotion/Style Tagged**: Each segment labeled with emotion and speaking style
- 🔊 **High Audio Quality**: 16kHz mono, normalized, no background music/noise
- ✅ **Thoroughly Reviewed**: Every segment manually listened to and quality-checked
- 🌐 **Diverse Sources**: 8 different YouTube sources across multiple content types

## Languages

- `en-IN`: Indian English
- `hi-IN`: Hindi

## Dataset Structure

### Data Fields

| Field | Type | Description |
|-------|------|-------------|
| `audio` | Audio | 16 kHz mono WAV clip |
| `transcript` | string | Manually reviewed and corrected transcript |
| `language_code` | string | Language code (en-IN or hi-IN) |
| `language_name` | string | Language name (Indian English or Hindi) |
| `bucket` | string | Language bucket (indian_english or hindi) |
| `emotion` | string | Emotion tag: neutral, happy, sad, excited, angry, serious, calm, concerned, other |
| `style` | string | Speaking style: conversational, formal, narration, interview, news, devotional, dramatic, other |
| `source_url` | string | Original YouTube source URL |
| `source_id` | string | Unique source identifier |
| `segment_id` | string | Unique segment identifier |
| `start_seconds` | float | Start timestamp in source video |
| `end_seconds` | float | End timestamp in source video |
| `duration_seconds` | float | Segment duration |
| `speaker_id` | string | Speaker identifier |
| `diarization_speaker_count` | int | Number of speakers detected (should be 1) |
| `quality_notes` | string | Manual quality notes |
| `reviewer_status` | string | Review status (all kept segments marked as "keep") |

### Emotion Distribution

The dataset includes a variety of emotional tones:
- **Neutral**: Informative, factual delivery
- **Happy**: Joyful, positive tone
- **Serious**: Grave, important topics
- **Excited**: Energetic, passionate delivery
- **Calm**: Peaceful, devotional content
- And more...

### Style Distribution

Multiple speaking styles are represented:
- **Formal**: Professional presentations, speeches
- **Conversational**: Natural dialogue, podcasts
- **News**: News anchors and commentary
- **Narration**: Storytelling
- **Devotional**: Spiritual/religious content

## Curation Process

### Pipeline Overview

1. **Source Selection** (8 YouTube videos)
   - TEDx talks
   - News segments
   - Podcast/speech content
   - Storytelling
   - Devotional content

2. **Segmentation** (72 candidate segments)
   - 20-70 second clips
   - Cut at natural speech boundaries
   - 16kHz mono conversion
   - Loudness normalization

3. **ASR & Diarization** (Sarvam API)
   - Sarvam Saaras v3 batch STT
   - Speaker diarization enabled
   - Language-specific processing

4. **Manual Review** (100% coverage)
   - Every segment manually listened to
   - Transcripts corrected (65% correction rate)
   - Quality assessment
   - Keep/reject decisions

5. **Final Selection** (63 segments kept, 9 rejected)
   - 87.5% acceptance rate
   - Quality over quantity approach
   - Balanced language distribution

### Quality Criteria

Segments were **kept** only if they met ALL criteria:
- ✅ Single speaker throughout
- ✅ Clear audio, no background music/noise
- ✅ Accurate, correctable transcript
- ✅ Natural prosody and intonation
- ✅ Complete sentences (no mid-word cuts)
- ✅ Appropriate duration (20-70 seconds)

Segments were **rejected** for:
- ❌ Multiple speakers detected
- ❌ Background music or noise
- ❌ Poor audio quality
- ❌ Clipped words at boundaries
- ❌ Uncorrectable transcripts

### Transcript Correction

**41 out of 63 transcripts (65%)** were manually corrected, including:
- Proper nouns (names, places)
- Numbers and dates
- Punctuation and grammar
- Language-specific corrections (Hindi diacritics)
- ASR artifacts

This high correction rate demonstrates thorough human curation and attention to quality.

## Source Attribution

All audio is sourced from YouTube with timestamps recorded for traceability:
- TEDx talks (typically CC BY-NC-ND licensed)
- News content (educational/research fair use)
- Public speeches and presentations
- Storytelling and devotional content

**Note**: Users should verify licensing terms for commercial use. The dataset creator has made reasonable efforts to select appropriately licensed content for educational and research purposes.

## Intended Use

### Primary Use Cases

- **TTS Model Training**: High-quality supervised training for Indian English and Hindi TTS
- **Speech Research**: Prosody, emotion, and style analysis
- **ASR Benchmarking**: Quality reference transcripts
- **Multilingual Studies**: Indian English and Hindi speech patterns

### Out of Scope

- Commercial TTS deployment without proper licensing verification
- Speaker identification or recognition tasks
- Dialect classification (covers general Indian English/Hindi)

## Limitations

- **Limited speaker diversity**: Multiple segments may feature same speakers
- **Domain coverage**: Primarily formal/professional content (news, talks, devotional)
- **Duration**: ~60 minutes is suitable for fine-tuning but not training from scratch
- **Single-speaker only**: No multi-speaker dialogue
- **Accent variation**: Limited regional accent diversity within languages

## Dataset Creation

### Curation Team

This dataset was curated as part of a Sarvam AI assignment by a single reviewer who:
- Selected all YouTube sources
- Defined segment boundaries
- Manually reviewed every audio clip
- Corrected all transcripts
- Made all quality decisions

### Tools Used

- **yt-dlp**: YouTube audio extraction
- **ffmpeg**: Audio processing and normalization
- **Sarvam Saaras v3**: Automatic speech recognition
- **Sarvam API**: Speaker diarization
- **Manual review**: Human quality assessment

### Annotations

**Transcripts**: Generated by Sarvam Saaras v3, then manually corrected (65% correction rate)

**Emotions/Styles**: Initially hinted in manifest, then manually verified during review

**Quality Status**: All segments manually reviewed and marked keep/reject

## Citation

If you use this dataset, please cite:

```
@misc{indian-tts-60min-2026,
  author = {Lochana Balivada},
  title = {Indian TTS YouTube Curated 60 Minute Dataset},
  year = {2026},
  publisher = {HuggingFace},
  howpublished = {\url{https://huggingface.co/datasets/lochanab30/indian-tts-60min}}
}
```

## License

This dataset is released under **CC BY-NC 4.0** (Creative Commons Attribution-NonCommercial 4.0 International).

You are free to:
- **Share**: Copy and redistribute
- **Adapt**: Remix, transform, and build upon

Under the following terms:
- **Attribution**: Must give appropriate credit
- **NonCommercial**: Not for commercial purposes without permission

## Contact

For questions or issues, please open an issue on the GitHub repository or contact via HuggingFace.

## Acknowledgments

- **Sarvam AI** for providing API access for ASR and diarization
- **HuggingFace** for dataset hosting platform
- **YouTube creators** for original content

---

**Dataset Version**: 1.0
**Created**: June 2026
**Last Updated**: June 7, 2026
