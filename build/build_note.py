#!/usr/bin/env python3
"""Assemble a per-lecture markdown note from manifest row + transcript + an authored summary.

Summaries are authored by Claude and passed in as a JSON sidecar:
  build/summaries/<slug>.json  ->  {"summary": "...", "key_points": ["...", ...], "language": "en"}
Run: build_note.py <manifest.json> <week|all>
Only builds notes for rows that are transcribed AND have a summary sidecar (English).
Non-English rows get a stub note (transcript kept, no summary) per the 'English only' rule.
"""
import json, os, re, sys
from glossary import apply_glossary

ROOT = "/Users/sree/Projects/HHIDSNotes"
NOTES = f"{ROOT}/notes"
SUMDIR = f"{ROOT}/build/summaries"
os.makedirs(SUMDIR, exist_ok=True)

def reflow(raw):
    """whisper emits one short phrase per line; join into readable paragraphs
    (~4 sentences each) split on sentence-ending punctuation."""
    text = re.sub(r"[ \t]+", " ", raw.replace("\n", " ")).strip()
    # split into sentences, keeping the terminator
    sentences = re.findall(r".+?(?:[.!?]+|$)", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    # collapse whisper repetition loops: drop a sentence if identical to the
    # previous one (case-insensitive), which removes runs like "X. X. X. X."
    deduped = []
    for s in sentences:
        if deduped and s.lower() == deduped[-1].lower():
            continue
        deduped.append(s)
    sentences = deduped
    paras, cur = [], []
    for s in sentences:
        cur.append(s)
        if len(cur) >= 4:
            paras.append(" ".join(cur)); cur = []
    if cur:
        paras.append(" ".join(cur))
    return "\n\n".join(paras)

def secs_to_hms(s):
    if not s: return None
    s = int(s); h, m, sec = s//3600, (s%3600)//60, s%60
    return f"{h}:{m:02d}:{sec:02d}" if h else f"{m}:{sec:02d}"

def yaml_str(s):
    if s is None: return '""'
    return '"' + str(s).replace('\\', '\\\\').replace('"', '\\"') + '"'

def build(row):
    slug = row["slug"]
    tf = row.get("transcript_path") or f"{ROOT}/build/transcripts/{slug}.txt"
    raw = open(tf, encoding="utf-8", errors="replace").read().strip() if os.path.exists(tf) else ""
    transcript = apply_glossary(reflow(raw))

    sidecar = f"{SUMDIR}/{slug}.json"
    summ = json.load(open(sidecar)) if os.path.exists(sidecar) else None
    lang = (summ or {}).get("language") or row.get("language")

    mdir = f"{NOTES}/module-{row['module_idx']}"
    os.makedirs(mdir, exist_ok=True)
    path = f"{mdir}/week-{int(row['week']):02d}-{slug}.md"

    dur = secs_to_hms(row.get("duration_sec")) or row.get("duration_str")
    fm = [
        "---",
        f"title: {yaml_str(row['title'])}",
        "speaker: Indradyumna Swami",
        f"week: {row['week']}",
        f"module: {yaml_str(row['module'])}",
        f"category: {yaml_str(row.get('category'))}",
        f"source: {yaml_str(row.get('source'))}",
        f"source_url: {yaml_str(row['link'])}",
        f"audio_url: {yaml_str(row.get('download_url'))}",
        f"duration: {yaml_str(dur)}",
        f"language: {yaml_str(lang)}",
        f"words: {row.get('words', len(transcript.split()))}",
        "transcribed_with: whisper.cpp large-v3-turbo",
        "---",
        "",
        f"# {row['title']}",
        "",
        f"**His Holiness Indradyumna Swami** · Week {row['week']} · {row.get('category') or ''} · {dur or ''}",
        "",
    ]
    if summ and summ.get("note"):
        fm.append(f"> _Note: {summ['note'].strip()}_")
        fm.append("")
    body = []
    if summ and lang == "en":
        body.append("## Summary\n")
        body.append(summ["summary"].strip() + "\n")
        kp = summ.get("key_points") or []
        if kp:
            body.append("## Key Points\n")
            body.extend(f"- {k}" for k in kp)
            body.append("")
        refs = summ.get("references") or []
        if refs:
            body.append("## Scriptural References\n")
            for r in refs:
                if isinstance(r, dict):
                    ref = (r.get("reference") or r.get("ref") or r.get("citation")
                           or r.get("scripture") or "")
                    note = r.get("note") or r.get("description") or r.get("cited_for") or ""
                    line = f"{ref} — {note}" if (ref and note) else (ref or note)
                else:
                    line = str(r)
                body.append(f"- {line}")
            body.append("")
    elif lang and lang != "en":
        body.append(f"> **Not summarized** — detected language `{lang}` (per the English-only rule). Full transcript kept below.\n")
    else:
        body.append("> _Summary pending._\n")

    body.append("## Transcript\n")
    body.append(transcript if transcript else "_(transcript unavailable)_")
    body.append("")
    body.append("---")
    body.append(
        "_© H.H. Indradyumna Swami / ISKCON; quoted scripture © BBT. All rights reserved. "
        "Machine-generated transcript and AI-generated summary — unofficial, unverified, and may "
        "contain errors; not the speaker's verbatim words. Non-commercial devotional study use only. "
        "See [DISCLAIMER](../../DISCLAIMER.md)._")
    body.append("")

    open(path, "w", encoding="utf-8").write("\n".join(fm) + "\n" + "\n".join(body) + "\n")
    return path, lang, bool(summ)

def main():
    man = sys.argv[1]
    sel = sys.argv[2:] or ["all"]
    rows = json.load(open(man))
    for row in rows:
        if row.get("status") != "transcribed":
            continue
        if "all" not in sel and str(row["week"]) not in sel:
            continue
        path, lang, has_sum = build(row)
        row["note_path"] = path
        print(f'wk{row["week"]:>3} lang={lang} sum={"Y" if has_sum else "-"} -> {path}')
    json.dump(rows, open(man, "w"), indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
