import subprocess, sys, time
pat=sys.argv[1]
while subprocess.run(["pgrep","-f",pat],capture_output=True).returncode==0:
    time.sleep=__import__('time').sleep
    time.sleep(20)
print("process gone:", pat)
