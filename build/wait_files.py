import os, sys, time
paths=sys.argv[1:]
while not all(os.path.exists(p) and os.path.getsize(p)>50 for p in paths):
    time.sleep(15)
print("all present:", len(paths))
