import sys, requests

if len(sys.argv) < 2:
    print("Not enough or valid arguments given. Please provide rurls")
    sys.exit(1)

found = False
for url in sys.argv[1:]:
    try:
        r = requests.get(url, timeout=5)
        latency = r.elapsed.total_seconds()
        statuscode = r.status_code
        print(url , statuscode, latency)
        if statuscode > 400:
            found = True
    except requests.exceptions.RequestException as e:
        print(url, "ERROR", type(e).__name__)
        found = True

if found:
    sys.exit(1)
else:
    sys.exit(0)


