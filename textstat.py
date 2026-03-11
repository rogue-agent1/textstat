#!/usr/bin/env python3
"""textstat - Text readability and complexity analyzer.

Single-file, zero-dependency CLI. Flesch-Kincaid, Coleman-Liau, SMOG, etc.
"""

import sys
import argparse
import re
import math


def count_syllables(word):
    word = word.lower().rstrip("e")
    if not word: return 1
    count = len(re.findall(r'[aeiouy]+', word))
    return max(1, count)


def analyze(text):
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    words = re.findall(r"[a-zA-Z']+", text)
    syllables = sum(count_syllables(w) for w in words)
    chars = sum(len(w) for w in words)
    complex_words = sum(1 for w in words if count_syllables(w) >= 3)

    n_sent = max(len(sentences), 1)
    n_words = max(len(words), 1)

    return {
        "sentences": n_sent, "words": n_words, "syllables": syllables,
        "chars": chars, "complex_words": complex_words,
        "avg_sentence_len": n_words / n_sent,
        "avg_syllables": syllables / n_words,
        "avg_word_len": chars / n_words,
    }


def flesch_reading_ease(s):
    return 206.835 - 1.015 * s["avg_sentence_len"] - 84.6 * s["avg_syllables"]


def flesch_kincaid_grade(s):
    return 0.39 * s["avg_sentence_len"] + 11.8 * s["avg_syllables"] - 15.59


def coleman_liau(s):
    L = s["chars"] / s["words"] * 100
    S = s["sentences"] / s["words"] * 100
    return 0.0588 * L - 0.296 * S - 15.8


def smog(s):
    if s["sentences"] < 3: return 0
    return 1.0430 * math.sqrt(s["complex_words"] * 30 / s["sentences"]) + 3.1291


def reading_level(score):
    if score >= 90: return "5th grade (very easy)"
    if score >= 80: return "6th grade (easy)"
    if score >= 70: return "7th grade (fairly easy)"
    if score >= 60: return "8th-9th grade (standard)"
    if score >= 50: return "10th-12th grade (fairly hard)"
    if score >= 30: return "College (hard)"
    return "Graduate (very hard)"


def cmd_analyze(args):
    text = open(args.file).read() if args.file else sys.stdin.read()
    s = analyze(text)
    fre = flesch_reading_ease(s)
    fkg = flesch_kincaid_grade(s)
    cli = coleman_liau(s)
    smog_idx = smog(s)

    print(f"  Text Statistics:")
    print(f"    Sentences:      {s['sentences']}")
    print(f"    Words:          {s['words']}")
    print(f"    Syllables:      {s['syllables']}")
    print(f"    Complex words:  {s['complex_words']} ({s['complex_words']/s['words']*100:.1f}%)")
    print(f"    Avg sentence:   {s['avg_sentence_len']:.1f} words")
    print(f"    Avg word:       {s['avg_word_len']:.1f} chars")
    print(f"\n  Readability Scores:")
    print(f"    Flesch Reading Ease:   {fre:.1f} — {reading_level(fre)}")
    print(f"    Flesch-Kincaid Grade:  {fkg:.1f}")
    print(f"    Coleman-Liau Index:    {cli:.1f}")
    if smog_idx:
        print(f"    SMOG Index:            {smog_idx:.1f}")


def main():
    p = argparse.ArgumentParser(prog="textstat", description="Text readability analyzer")
    sub = p.add_subparsers(dest="cmd")
    s = sub.add_parser("analyze", aliases=["a"], help="Analyze text")
    s.add_argument("-f", "--file")
    args = p.parse_args()
    if not args.cmd: p.print_help(); return 1
    cmds = {"analyze": cmd_analyze, "a": cmd_analyze}
    return cmds[args.cmd](args) or 0


if __name__ == "__main__":
    sys.exit(main())
