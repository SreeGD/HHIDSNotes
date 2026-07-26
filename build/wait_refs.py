import json, os, sys, time
sc = sys.argv[1]
while True:
    if os.path.exists(sc):
        try:
            d = json.load(open(sc))
            if d.get('references'):
                print(f"{sc}: {len(d['references'])} references present"); break
        except Exception:
            pass
    time.sleep(15)
