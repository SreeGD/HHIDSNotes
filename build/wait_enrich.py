import json, os, time
slugs=json.load(open('/tmp/enrich_slugs.json'))
keys=('themes','stories','quotes','glossary')
while True:
    missing=[]
    for s in slugs:
        p=f"summaries/{s}.json"
        try:
            d=json.load(open(p))
            if not all(k in d for k in keys): missing.append(s)
        except Exception: missing.append(s)
    if not missing:
        print(f"ALL {len(slugs)} enriched with themes/stories/quotes/glossary"); break
    time.sleep(20)
