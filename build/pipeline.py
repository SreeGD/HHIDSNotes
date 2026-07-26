#!/usr/bin/env python3
"""Resumable transcription pipeline: download -> 16k wav -> whisper turbo -> lang detect.
Usage: pipeline.py <manifest.json> <week|all|kind:xxx> [more weeks...]
Only does the mechanical part (transcript + detected language). Summaries/notes are authored separately.
"""
import json, os, re, subprocess, sys, time

ROOT = "/Users/sree/Projects/HHIDSNotes"
AUDIO = f"{ROOT}/audio"
TXDIR = f"{ROOT}/build/transcripts"
MODEL = "/Users/sree/.cache/whisper/ggml-large-v3-turbo.bin"
VAD_MODEL = "/Users/sree/.cache/whisper/ggml-silero-v5.1.2.bin"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15"
os.makedirs(AUDIO, exist_ok=True)
os.makedirs(TXDIR, exist_ok=True)

def run(cmd, **kw):
    return subprocess.run(cmd, **kw)

def download(row):
    slug = row["slug"]
    url = row["download_url"]
    out = f"{AUDIO}/{slug}"
    if row["kind"] == "youtube":
        # grab bestaudio, remux to mp3. YouTube 403s on default client; android_vr works.
        target = f"{out}.mp3"
        if os.path.exists(target):
            return target
        for client in ("android_vr", "tv", "web", "ios"):
            r = run(["yt-dlp", "--no-warnings",
                     "--extractor-args", f"youtube:player_client={client}",
                     "-f", "bestaudio/best",
                     "-x", "--audio-format", "mp3", "--audio-quality", "5",
                     "-o", f"{out}.%(ext)s", url])
            if r.returncode == 0 and os.path.exists(target):
                return target
        return None
    else:  # direct mp3 (narottam podpress or IDT)
        target = f"{out}.mp3"
        if os.path.exists(target) and os.path.getsize(target) > 10000:
            return target
        r = run(["curl", "-sL", "--fail", "-A", UA, "-o", target, url])
        return target if r.returncode == 0 and os.path.exists(target) and os.path.getsize(target) > 10000 else None

def to_wav(mp3):
    wav = mp3.rsplit(".", 1)[0] + ".16k.wav"
    if os.path.exists(wav):
        return wav
    r = run(["ffmpeg", "-y", "-i", mp3, "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", wav],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return wav if r.returncode == 0 and os.path.exists(wav) else None

def transcribe(wav, slug):
    of = f"{TXDIR}/{slug}"
    # -mc 0 (max-context 0) + VAD strongly suppress whisper repetition/hallucination loops
    r = run(["whisper-cli", "-m", MODEL, "-l", "auto", "-t", "8",
             "-mc", "0", "--vad", "-vm", VAD_MODEL,
             "-oj", "-otxt", "-of", of, "-np", wav],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    jf, tf = of + ".json", of + ".txt"
    if not os.path.exists(jf):
        return None, None
    # whisper.cpp can emit stray non-UTF8 bytes; never let that crash the run
    j = json.load(open(jf, encoding="utf-8", errors="replace"))
    lang = (j.get("result") or {}).get("language")
    text = open(tf, encoding="utf-8", errors="replace").read().strip() if os.path.exists(tf) else ""
    return lang, text

def process(row):
    slug = row["slug"]
    tf = f"{TXDIR}/{slug}.txt"
    if os.path.exists(tf) and os.path.getsize(tf) > 40 and row.get("language"):
        return "cached"
    t0 = time.time()
    mp3 = download(row)
    if not mp3:
        row["status"] = "download_failed"; return "download_failed"
    # duration
    try:
        d = subprocess.run(["ffprobe","-v","quiet","-show_entries","format=duration","-of","csv=p=0",mp3],
                           capture_output=True, text=True)
        row["duration_sec"] = round(float(d.stdout.strip()))
    except Exception:
        row["duration_sec"] = None
    wav = to_wav(mp3)
    if not wav:
        row["status"] = "convert_failed"; return "convert_failed"
    lang, text = transcribe(wav, slug)
    # cleanup big files
    for f in (mp3, wav):
        try: os.remove(f)
        except OSError: pass
    if not text:
        row["status"] = "transcribe_failed"; return "transcribe_failed"
    row["language"] = lang
    row["words"] = len(text.split())
    row["transcript_path"] = tf
    row["status"] = "transcribed"
    row["elapsed_sec"] = round(time.time() - t0)
    return f"OK lang={lang} words={row['words']} dur={row.get('duration_sec')}s elapsed={row['elapsed_sec']}s"

def main():
    man = sys.argv[1]
    sel = sys.argv[2:]
    rows = json.load(open(man))
    def match(r):
        if "all" in sel: return True
        for s in sel:
            if s.startswith("kind:") and r["kind"] == s[5:]: return True
            if s.isdigit() and r["week"] == int(s): return True
        return False
    todo = [r for r in rows if match(r) and r.get("download_url")]
    print(f"[{time.strftime('%H:%M:%S')}] processing {len(todo)} rows", flush=True)
    for r in todo:
        print(f"[{time.strftime('%H:%M:%S')}] wk{r['week']} {r['title'][:40]!r} ({r['kind']}) ...", flush=True)
        try:
            res = process(r)
        except Exception as e:
            r["status"] = "error"
            r["error"] = f"{type(e).__name__}: {e}"
            res = f"ERROR {r['error']}"
        print(f"    -> {res}", flush=True)
        json.dump(rows, open(man, "w"), indent=2, ensure_ascii=False)  # save after each
    print(f"[{time.strftime('%H:%M:%S')}] done", flush=True)

if __name__ == "__main__":
    main()
