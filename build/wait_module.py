import json, sys, time
mod = int(sys.argv[1])
while True:
    rows = json.load(open('manifest.json'))
    mrows = [r for r in rows if r['module_idx']==mod and r.get('download_url')]
    pend = [r for r in mrows if r['status']=='pending']
    if not pend:
        done=[r for r in mrows if r['status']=='transcribed']
        print(f"MODULE {mod} COMPLETE: {len(done)}/{len(mrows)} transcribed")
        for r in mrows:
            if r['status']!='transcribed':
                print(f"  wk{r['week']} {r['status']}: {r['title'][:40]}")
        break
    time.sleep(30)
