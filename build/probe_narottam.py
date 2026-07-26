#!/usr/bin/env python3
"""Classify each narottam.com link: text transcript vs audio post. Extract mp3 URL if audio."""
import json, re, sys, urllib.request
from bs4 import BeautifulSoup

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15"

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read().decode("utf-8", errors="replace")

def probe(url):
    try:
        html = fetch(url)
    except Exception as e:
        return {"error": str(e)}
    soup = BeautifulSoup(html, "lxml")
    ec = soup.find(class_=re.compile(r"\bentry-content\b")) or soup.find("article") or soup.body
    # find mp3 links anywhere in the post content
    mp3s = []
    for a in ec.find_all("a", href=True):
        if ".mp3" in a["href"].lower():
            mp3s.append(a["href"])
    if not mp3s:
        for m in re.findall(r'https?://[^\s"\'<>]+?\.mp3', html):
            mp3s.append(m)
    mp3s = list(dict.fromkeys(mp3s))
    # body text without the audio-player div
    for bad in ec.find_all(class_=re.compile("podPress", re.I)):
        bad.decompose()
    for bad in ec.find_all(["script", "style"]):
        bad.decompose()
    body = ec.get_text(" ", strip=True)
    words = len(body.split())
    return {"words": words, "mp3": mp3s[0] if mp3s else None, "n_mp3": len(mp3s)}

if __name__ == "__main__":
    manifest = json.load(open(sys.argv[1]))
    for row in manifest:
        if row["kind"] != "article":
            continue
        info = probe(row["link"])
        row["probe"] = info
        klass = "AUDIO" if info.get("mp3") else ("TEXT" if info.get("words",0) > 200 else "THIN")
        print(f'{row["week"]:>3} [{klass:5}] words={info.get("words","?"):>5} mp3={"Y" if info.get("mp3") else "-"}  {row["title"][:45]}')
    json.dump(manifest, open(sys.argv[1], "w"), indent=2, ensure_ascii=False)
