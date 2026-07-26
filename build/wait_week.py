import json, sys, time
wk=int(sys.argv[1])
while True:
    r=next(x for x in json.load(open('manifest.json')) if x['week']==wk)
    if r['status']!='pending':
        print(f"wk{wk}: {r['status']} lang={r.get('language')} words={r.get('words')} err={r.get('error','')}")
        break
    time.sleep(10)
