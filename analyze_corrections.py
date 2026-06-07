#!/usr/bin/env python3
"""
Run this AFTER manual review to analyze transcript corrections.
Usage: python3 analyze_corrections.py
"""

import csv
from difflib import SequenceMatcher

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def main():
    with open('metadata/manual_review.csv', 'r') as f:
        rows = list(csv.DictReader(f))

    corrections = []
    for row in rows:
        if row['review_status'] != 'keep':
            continue  # Only analyze kept segments

        original = row.get('transcript', '').strip()
        corrected = row.get('corrected_transcript', '').strip()

        if original and corrected and original != corrected:
            sim = similarity(original, corrected)
            corrections.append({
                'segment_id': row['segment_id'],
                'original': original[:100],
                'corrected': corrected[:100],
                'similarity': sim,
                'change_type': 'minor' if sim > 0.9 else 'major'
            })

    print("=" * 70)
    print("TRANSCRIPT CORRECTION ANALYSIS")
    print("=" * 70)
    print(f"\nTotal kept segments: {len([r for r in rows if r['review_status'] == 'keep'])}")
    print(f"Segments with corrections: {len(corrections)}")
    print(f"Correction rate: {len(corrections) / len([r for r in rows if r['review_status'] == 'keep']) * 100:.1f}%")

    minor = [c for c in corrections if c['change_type'] == 'minor']
    major = [c for c in corrections if c['change_type'] == 'major']

    print(f"\nMinor corrections (>90% similar): {len(minor)}")
    print(f"Major corrections (<90% similar): {len(major)}")

    print("\n" + "=" * 70)
    print("EXAMPLES OF CORRECTIONS (for report):")
    print("=" * 70)

    # Show a few examples
    for i, corr in enumerate(corrections[:5]):
        print(f"\n{i+1}. {corr['segment_id']} ({corr['change_type']} correction):")
        print(f"   Original:  {corr['original']}...")
        print(f"   Corrected: {corr['corrected']}...")

    print("\n" + "=" * 70)
    print("Add this to your report's 'Iterations' section!")
    print("=" * 70)

if __name__ == '__main__':
    main()
