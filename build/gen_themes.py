#!/usr/bin/env python3
"""Generate THEMES.md — a thematic index of all English lectures.
Major Themes (>=3 lectures) + full A-Z index; light normalization merges variants."""
import json, os, glob, re
from collections import defaultdict

ROOT = "/Users/sree/Projects/HHIDSNotes"
rows = {r['slug']: r for r in json.load(open(f"{ROOT}/build/manifest.json"))}

# explicit synonym -> canonical merges for obvious duplicates
SYN = {
    "sankirtan": "sankirtana", "sankirtana": "sankirtana", "harinam sankirtan": "sankirtana",
    "kirtana": "kirtan",
    "sadhu sanga": "sadhu-sanga", "sadhu-sanga": "sadhu-sanga",
    "association of devotees": "sadhu-sanga", "association with devotees": "sadhu-sanga",
    "power of association": "sadhu-sanga", "devotee association": "sadhu-sanga",
    "guru and disciple": "guru-disciple relationship",
    "guru & disciple": "guru-disciple relationship",
    "guru-disciple relationship": "guru-disciple relationship",
    "guru-disciple": "guru-disciple relationship",
    "srila prabhupada's sacrifice": "srila prabhupada",
    "the holy name": "holy name", "glories of the holy name": "holy name",
    "holy names": "holy name",
    "chanting the holy name": "chanting",
    "book distribution": "book distribution", "distributing books": "book distribution",
}

def norm(t):
    t = re.sub(r"\s+", " ", t.strip().lower())
    return SYN.get(t, t)

theme_lects = defaultdict(set)  # theme -> set(slug)
for sc in glob.glob(f"{ROOT}/build/summaries/*.json"):
    d = json.load(open(sc))
    if d.get("language") != "en":
        continue
    slug = os.path.basename(sc)[:-5]
    for t in d.get("themes", []):
        theme_lects[norm(t)].add(slug)

def link(slug):
    r = rows[slug]
    stem = f"notes/module-{r['module_idx']}/week-{int(r['week']):02d}-{slug}.md"
    title = r['title'].replace('|', '\\|').replace('[', '(').replace(']', ')')
    return (int(r['week']), f"[wk{r['week']} {title}]({stem})")

def lect_list(slugs):
    return " · ".join(l for _, l in sorted((link(s) for s in slugs), key=lambda x: x[0]))

lines = ["# Thematic Index",
         "",
         "Browse the course by topic. Themes are drawn from the tags on each lecture note "
         "(variants merged). Each entry links to the enriched note.",
         ""]

major = sorted(((t, s) for t, s in theme_lects.items() if len(s) >= 3),
               key=lambda x: (-len(x[1]), x[0]))
lines.append("## Major Themes")
lines.append("")
lines.append(f"Topics spanning three or more lectures ({len(major)} themes).")
lines.append("")
for t, slugs in major:
    lines.append(f"### {t.title()} ({len(slugs)})")
    lines.append(lect_list(slugs))
    lines.append("")

lines.append("## All Themes (A–Z)")
lines.append("")
for t in sorted(theme_lects):
    lines.append(f"- **{t}** — {lect_list(theme_lects[t])}")
lines.append("")

open(f"{ROOT}/THEMES.md", "w", encoding="utf-8").write("\n".join(lines) + "\n")
print(f"THEMES.md: {len(theme_lects)} themes, {len(major)} major themes")
print("top major:", [(t, len(s)) for t, s in major[:8]])
