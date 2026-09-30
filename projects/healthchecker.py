import sys, requests


if len(sys.argv) < 2:
    print("Enter healthchecker.py and urls you want to check")
    sys.exit(1)

found = False
for url in sys.argv[1:]:
    try:
        response = requests.get(url, timeout=5)
        statuscode = response.status_code
        latency = response.elapsed.total_seconds()
        print(url, statuscode, latency)
        if statuscode >= 400:
            found = True

    except requests.exceptions.RequestException as e:
        print(url, "ERROR", type(e).__name__)
        found = True
    
if found:
    sys.exit(1)
else:
    sys.exit(0)


