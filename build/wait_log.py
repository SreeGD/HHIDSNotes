import sys, time
logf=sys.argv[1]; needle=sys.argv[2]
while True:
    try:
        if needle in open(logf,encoding='utf-8',errors='replace').read():
            print(f"'{needle}' found in {logf}"); break
    except FileNotFoundError: pass
    time.sleep(20)
