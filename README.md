# HH IDS Notes — Pre-Initiation Course Lecture Notes

Study notes for the **Pre-Initiation IDS course** — 80 lectures by **His Holiness Indradyumna Swami** — organized into 5 modules. Each lecture was downloaded, transcribed, and enriched into a markdown note with a summary, key points, and scriptural references.

## What's here

```
notes/module-1..5/      one markdown note per lecture (79 notes)
build/                  the pipeline that produced them
  ├─ manifest.json      per-lecture metadata + processing state
  ├─ summaries/         authored summary/key-points/references (JSON, per lecture)
  ├─ transcripts/       raw whisper transcripts (.txt, source of truth)
  ├─ pipeline.py        download → 16k wav → whisper transcribe → language detect
  ├─ build_note.py      assemble a note from transcript + summary
  ├─ update_xlsx.py     write summaries into the course spreadsheet
  ├─ glossary.py        light auto-correct of common mis-heard Sanskrit terms
  └─ Pre-Initiation_IDS_course_modules.xlsx   the source spreadsheet with Summary column filled
```

Each **English** note contains: YAML front-matter (title, week, module, category, source/audio URLs, duration, detected language) → **Summary** → **Key Points** → **Scriptural References** → the full reflowed **Transcript**.

## How it was made

- **Transcription:** local [whisper.cpp](https://github.com/ggerganov/whisper.cpp) with the `large-v3-turbo` model, `--max-context 0` + Silero VAD (to suppress repetition-hallucination loops), auto language-detection.
- **Summaries & references:** generated from the transcripts and normalized to standard ISKCON/Gaudiya Vaishnava spellings; verse numbers are given where identifiable and hedged otherwise.
- **Corpus:** ~83 hours of audio, ~550,000 transcript words.

## Coverage & caveats

- **65 lectures** are in English and fully enriched (summary + key points + references).
- **12 lectures** are non-English (11 Russian, 1 Polish) — transcript kept, flagged, **not** summarized.
- **2 lectures** (Module 3 wk34, wk35) are SoundCloud placeholders with no audio link yet — stub notes only.
- Transcripts are **machine-generated** and may contain errors in proper nouns and Sanskrit terms. They are unofficial study aids, not authorized publications.

## Attribution

All lectures are by **H.H. Indradyumna Swami**. Source audio comes from [narottam.com](https://narottam.com), ISKCON Desire Tree, YouTube, and SoundCloud, where it is shared for the purpose of preaching Krishna consciousness. These notes are a devotional study project.
