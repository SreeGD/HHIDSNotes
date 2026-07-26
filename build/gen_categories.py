#!/usr/bin/env python3
"""Generate CATEGORIES.md — a category index of all lectures (from the sheet's Category column)."""
import json, os
from collections import defaultdict

ROOT = "/Users/sree/Projects/HHIDSNotes"
rows = json.load(open(f"{ROOT}/build/manifest.json"))

def is_en(r):
    sc = f"{ROOT}/build/summaries/{r['slug']}.json"
    return os.path.exists(sc) and json.load(open(sc)).get("language") == "en"

def marker(r):
    if r.get("link") == "link_placeholder":
        return "—"  # no audio
    if is_en(r):
        return "EN"
    return {"ru": "RU", "pl": "PL"}.get(r.get("language"), "EN")

def link(r):
    stem = f"notes/module-{r['module_idx']}/week-{int(r['week']):02d}-{r['slug']}.md"
    title = r['title'].replace('|', '\\|').replace('[', '(').replace(']', ')')
    return f"| {r['week']} | [{title}]({stem}) | Module {r['module_idx']} | {marker(r)} |"

by_cat = defaultdict(list)
for r in rows:
    cat = (r.get("category") or "").strip() or "Uncategorized"
    by_cat[cat].append(r)

# preferred order: the two named course categories, then Uncategorized
order = [c for c in ["Foundations in Bhakti", "Festivals and Kirtans"] if c in by_cat]
order += [c for c in sorted(by_cat) if c not in order]

lines = ["# Category Index",
         "",
         "Lectures grouped by the course **Category** (from the source spreadsheet). "
         "`EN` = English (enriched note); `RU`/`PL` = non-English (transcript only); `—` = placeholder (no audio yet).",
         ""]
# quick counts line
counts = " · ".join(f"{c} ({len(by_cat[c])})" for c in order)
lines += [counts, ""]

for cat in order:
    rs = sorted(by_cat[cat], key=lambda x: x['week'])
    lines.append(f"## {cat} ({len(rs)})")
    lines.append("")
    lines.append("| Wk | Title | Module | Lang |")
    lines.append("|---:|-------|--------|:----:|")
    lines += [link(r) for r in rs]
    lines.append("")

open(f"{ROOT}/CATEGORIES.md", "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("CATEGORIES.md:", {c: len(by_cat[c]) for c in order})
