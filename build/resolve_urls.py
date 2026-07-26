#!/usr/bin/env python3
"""Add download_url + (where known) duration to each manifest row."""
import json, re, sys, urllib.request
from bs4 import BeautifulSoup
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15"

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read().decode("utf-8", errors="replace")

man = sys.argv[1]
rows = json.load(open(man))
for row in rows:
    k = row["kind"]
    if k == "audio_mp3":
        row["download_url"] = row["link"]
    elif k in ("youtube",):
        row["download_url"] = row["link"]
    elif k == "article":
        # already probed: mp3 url + maybe duration text like [ 1:24:00 ]
        mp3 = (row.get("probe") or {}).get("mp3")
        row["download_url"] = mp3
        try:
            html = fetch(row["link"])
            m = re.search(r"\[\s*(\d{1,2}:\d{2}(?::\d{2})?)\s*\]", html)
            row["duration_str"] = m.group(1) if m else None
        except Exception as e:
            row["duration_str"] = None
    else:
        row["download_url"] = None
json.dump(rows, open(man, "w"), indent=2, ensure_ascii=False)

def dsec(s):
    if not s: return None
    p=[int(x) for x in s.split(":")]
    return p[0]*3600+p[1]*60+p[2] if len(p)==3 else p[0]*60+p[1]
print("Narottam durations (parsed from page):")
for r in sorted([x for x in rows if x["kind"]=="article"], key=lambda x:(dsec(x.get("duration_str")) or 99999)):
    print(f'  {r["week"]:>3}  {r.get("duration_str") or "?":>8}  {r["title"][:45]}')
