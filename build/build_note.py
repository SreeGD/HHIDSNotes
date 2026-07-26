#!/usr/bin/env python3
"""Assemble, per lecture, TWO separate files:
  1. an ENRICHED note   -> notes/module-N/week-XX-slug.md      (summary + key points + scriptural references, links to transcript)
  2. a TRANSCRIPT file   -> transcripts/module-N/week-XX-slug.md (full transcript kept as-is; verbatim, no glossary edits)

Summaries are authored separately as JSON sidecars:
  build/summaries/<slug>.json -> {"language","summary","key_points","references"[,"note"]}
Run: build_note.py <manifest.json> <week|all>
"""
import json, os, re, sys

ROOT = "/Users/sree/Projects/HHIDSNotes"
NOTES = f"{ROOT}/notes"
TXOUT = f"{ROOT}/transcripts"
SUMDIR = f"{ROOT}/build/summaries"
STRUCT = f"{ROOT}/build/structured"
os.makedirs(SUMDIR, exist_ok=True)
os.makedirs(STRUCT, exist_ok=True)

DISCLAIMER = (
    "_© H.H. Indradyumna Swami / ISKCON; quoted scripture © BBT. All rights reserved. "
    "Machine-generated transcript and AI-generated summary — unofficial, unverified, and may "
    "contain errors; not the speaker's verbatim words. Non-commercial devotional study use only. "
    "See [DISCLAIMER](../../DISCLAIMER.md)._")

def reflow(raw):
    """whisper emits one short phrase per line; join into readable paragraphs
    (~4 sentences each) WITHOUT altering words (kept as-is)."""
    text = re.sub(r"[ \t]+", " ", raw.replace("\n", " ")).strip()
    sentences = [s.strip() for s in re.findall(r".+?(?:[.!?]+|$)", text) if s.strip()]
    # collapse pure whisper repetition loops (identical consecutive sentences) only
    deduped = []
    for s in sentences:
        if deduped and s.lower() == deduped[-1].lower():
            continue
        deduped.append(s)
    paras, cur = [], []
    for s in deduped:
        cur.append(s)
        if len(cur) >= 4:
            paras.append(" ".join(cur)); cur = []
    if cur:
        paras.append(" ".join(cur))
    return "\n\n".join(paras)

def secs_to_hms(s):
    if not s: return None
    s = int(s); h, m, sec = s // 3600, (s % 3600) // 60, s % 60
    return f"{h}:{m:02d}:{sec:02d}" if h else f"{m}:{sec:02d}"

def yaml_str(s):
    if s is None: return '""'
    return '"' + str(s).replace('\\', '\\\\').replace('"', '\\"') + '"'

def frontmatter(row, lang, words, dur, kind, tags=None):
    fm = [
        "---",
        f"title: {yaml_str(row['title'])}",
        f"kind: {kind}",
        "speaker: Indradyumna Swami",
        f"week: {row['week']}",
        f"module: {yaml_str(row['module'])}",
        f"category: {yaml_str(row.get('category'))}",
        f"source: {yaml_str(row.get('source'))}",
        f"source_url: {yaml_str(row['link'])}",
        f"audio_url: {yaml_str(row.get('download_url'))}",
        f"duration: {yaml_str(dur)}",
        f"language: {yaml_str(lang)}",
        f"words: {words}",
        "transcribed_with: whisper.cpp large-v3-turbo",
    ]
    if tags:
        fm.append("tags: [" + ", ".join(yaml_str(t) for t in tags) + "]")
    fm += ["---", ""]
    return fm

def glossary_line(g):
    if isinstance(g, dict):
        term = g.get("term") or g.get("name") or ""
        meaning = g.get("meaning") or g.get("definition") or g.get("desc") or ""
        return f"**{term}** — {meaning}" if (term and meaning) else (term or meaning)
    return str(g)

def build(row):
    slug = row["slug"]
    tf = row.get("transcript_path") or f"{ROOT}/build/transcripts/{slug}.txt"
    raw = open(tf, encoding="utf-8", errors="replace").read().strip() if os.path.exists(tf) else ""
    transcript = reflow(raw)  # kept as-is: verbatim words, only wrapped into paragraphs

    summ = None
    sc = f"{SUMDIR}/{slug}.json"
    if os.path.exists(sc):
        summ = json.load(open(sc))
    lang = (summ or {}).get("language") or row.get("language")
    words = row.get("words", len(transcript.split()))
    dur = secs_to_hms(row.get("duration_sec")) or row.get("duration_str")

    stem = f"module-{row['module_idx']}/week-{int(row['week']):02d}-{slug}.md"
    note_path = f"{NOTES}/{stem}"
    tx_path = f"{TXOUT}/{stem}"
    os.makedirs(os.path.dirname(note_path), exist_ok=True)
    os.makedirs(os.path.dirname(tx_path), exist_ok=True)
    tx_link = f"../../transcripts/{stem}"
    note_link = f"../../notes/{stem}"

    themes = (summ or {}).get("themes") or []
    # ---------- ENRICHED NOTE (no transcript body) ----------
    out = frontmatter(row, lang, words, dur, "enriched-note", tags=(themes if lang == "en" else None))
    out += [f"# {row['title']}", "",
            f"**His Holiness Indradyumna Swami** · Week {row['week']} · {row.get('category') or ''} · {dur or ''}", ""]
    if summ and summ.get("note"):
        out += [f"> _Note: {summ['note'].strip()}_", ""]
    if summ and lang == "en":
        if themes:
            out += ["**Themes:** " + " · ".join(themes), ""]
        out += ["## Summary", "", summ["summary"].strip(), ""]
        # Structured notes body: full sectioned walkthrough of the lecture
        # (all content, scriptural references inline). Written per-lecture to
        # build/structured/<slug>.md by the enrichment agents.
        sf = f"{STRUCT}/{slug}.md"
        body_md = open(sf, encoding="utf-8", errors="replace").read().strip() if os.path.exists(sf) else ""
        if body_md:
            # full structured walkthrough (references inline)
            out += [body_md, ""]
        else:
            # fallback until the structured notes for this lecture are generated
            if summ.get("key_points"):
                out += ["## Key Points", ""] + [f"- {k}" for k in summ["key_points"]] + [""]
            if summ.get("stories"):
                out += ["## Notable Stories & Analogies", ""] + [f"- {s}" for s in summ["stories"]] + [""]
            if summ.get("quotes"):
                out += ["## Memorable Quotes", ""] + [f"> “{str(q).strip().strip(chr(8220)+chr(8221)+chr(34))}”" for q in summ["quotes"]] + [""]
        refs = summ.get("references") or []
        if refs:
            out += ["## Scriptural References", ""]
            for r in refs:
                if isinstance(r, dict):
                    ref = (r.get("reference") or r.get("ref") or r.get("citation") or r.get("scripture") or "")
                    note = r.get("note") or r.get("description") or r.get("cited_for") or ""
                    line = f"{ref} — {note}" if (ref and note) else (ref or note)
                else:
                    line = str(r)
                out.append(f"- {line}")
            out.append("")
        if summ.get("glossary"):
            out += ["## Glossary", ""] + [f"- {glossary_line(g)}" for g in summ["glossary"]] + [""]
    elif lang and lang != "en":
        out += [f"> **Not summarized** — detected language `{lang}` (per the English-only rule). "
                "The transcript is kept separately.", ""]
    else:
        out += ["> _Summary pending._", ""]
    out += [f"📄 **Full transcript:** [{os.path.basename(tx_path)}]({tx_link})", "",
            "---", DISCLAIMER, ""]
    open(note_path, "w", encoding="utf-8").write("\n".join(out) + "\n")

    # ---------- TRANSCRIPT (kept as-is) ----------
    tout = frontmatter(row, lang, words, dur, "transcript")
    tout += [f"# {row['title']} — Transcript", "",
             f"**His Holiness Indradyumna Swami** · Week {row['week']} · {dur or ''}", "",
             f"> Verbatim machine transcript (whisper.cpp large-v3-turbo), kept as-is and unedited; "
             f"it may contain errors and is not the speaker's exact words. "
             f"Enriched note: [{os.path.basename(note_path)}]({note_link}).", "",
             "---", "",
             transcript if transcript else "_(transcript unavailable)_", "",
             "---", DISCLAIMER, ""]
    open(tx_path, "w", encoding="utf-8").write("\n".join(tout) + "\n")

    return note_path, tx_path, lang, bool(summ)

def main():
    man = sys.argv[1]
    sel = sys.argv[2:] or ["all"]
    rows = json.load(open(man))
    for row in rows:
        if row.get("status") != "transcribed":
            continue
        if "all" not in sel and str(row["week"]) not in sel:
            continue
        note_path, tx_path, lang, has_sum = build(row)
        row["note_path"] = note_path
        row["transcript_note_path"] = tx_path
        print(f'wk{row["week"]:>3} lang={lang} sum={"Y" if has_sum else "-"} -> note + transcript')
    json.dump(rows, open(man, "w"), indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
