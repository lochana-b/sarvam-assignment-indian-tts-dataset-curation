# Quick Manual Review Guide

**You need to review 70 segments** (2 already marked reject)

## Your Streamlined Process:

### For EACH segment:

1. **Play audio** (click audio_path in CSV)
2. **Listen while reading corrected_transcript**
3. **Fix transcript** if ASR made mistakes
4. **Quick quality check:**
   - ✅ Single speaker only?
   - ✅ Clear audio, no background noise?
   - ✅ Natural speech?
   - ✅ Doesn't cut mid-word?
5. **Set review_status:**
   - `keep` = Good quality
   - `reject` = Has issues
6. **Add quality_notes** if rejecting

## Speed Tips:

- **If everything sounds good:** Just change `needs_review` → `keep`
- **If transcript is correct:** Don't edit corrected_transcript
- **If obvious problem:** Mark `reject` and move on quickly
- **Don't overthink:** Trust your ears

## Quality Bar:

**KEEP if:**
- Single speaker
- Clear audio
- Accurate transcript (or you fixed it)
- Natural speech

**REJECT if:**
- Multiple speakers
- Background music/noise
- Poor quality
- Cuts off words
- Can't understand

## Time Estimate:

- **Fast segments:** 30 seconds (just listen, mark keep)
- **Problem segments:** 2 minutes (listen, decide reject)
- **Transcript fixes:** 1-2 minutes (listen multiple times, correct)

**Average:** ~1-2 minutes per segment = **2-3 hours total**

## Goal:

Keep 45-55 good segments out of 70 = ~50-55 minutes final dataset

---

**Just be honest about quality. The evaluators want to see your judgment!**
