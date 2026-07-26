import json, os, time
lst=json.load(open('/tmp/struct_list.json'))
slugs=[x['slug'] for x in lst]
while True:
    missing=[s for s in slugs if not (os.path.exists(f"structured/{s}.md") and os.path.getsize(f"structured/{s}.md")>200)]
    if not missing:
        print(f"ALL {len(slugs)} structured notes written"); break
    time.sleep(30)
