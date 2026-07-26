#!/usr/bin/env python3
"""Write authored summaries into the Summary column (E) of the workbook, preserving everything else.
Reads build/summaries/<slug>.json for English summaries; marks non-English rows.
Run: update_xlsx.py <manifest.json> <target.xlsx>
"""
import json, os, sys, openpyxl

ROOT = "/Users/sree/Projects/HHIDSNotes"
SUMDIR = f"{ROOT}/build/summaries"

def main():
    man, xlsx = sys.argv[1], sys.argv[2]
    rows = json.load(open(man))
    by_key = {(r["module"], r["sheet_row"]): r for r in rows}
    wb = openpyxl.load_workbook(xlsx)

    def unmerge_col_e(ws, r):
        """If E{r} sits inside a merged range (e.g. D:F merged), split it so the
        link stays in D{r} and E{r} becomes writable."""
        for rng in list(ws.merged_cells.ranges):
            if rng.min_row <= r <= rng.max_row and rng.min_col <= 5 <= rng.max_col:
                ws.unmerge_cells(str(rng))

    updated = 0
    for ws in wb.worksheets:
        for r in range(2, ws.max_row + 1):
            row = by_key.get((ws.title, r))
            if not row:
                continue
            slug = row["slug"]
            sidecar = f"{SUMDIR}/{slug}.json"
            text = None
            if os.path.exists(sidecar):
                s = json.load(open(sidecar))
                if s.get("language") == "en":
                    text = s["summary"].strip()
            elif row.get("language") and row["language"] != "en":
                text = f"[Not summarized — detected {row['language']}]"
            elif row.get("link") == "link_placeholder":
                text = "[No audio link — supply the SoundCloud/audio URL to transcribe]"
            elif row.get("status") == "download_failed":
                text = "[Download pending — retrying audio source]"
            if text is not None:
                unmerge_col_e(ws, r)
                ws.cell(r, 5).value = text
                ws.cell(r, 5).alignment = openpyxl.styles.Alignment(wrap_text=True, vertical="top")
                updated += 1
    wb.save(xlsx)
    print(f"updated {updated} Summary cells in {xlsx}")

if __name__ == "__main__":
    main()
