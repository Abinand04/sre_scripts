# healthchecker

A command line script that checks the health of a list of URLs. It reports
the status code and latency for each, and the error type for any that fail.

## Usage

````bash
python3 healthchecker.py url1 url2 url3 ...
````

At least one URL is required.

## Example

````bash
$ python3 healthchecker.py https://example.com https://httpstat.us/500 https://notarealhost.xyz
https://example.com 200 0.10855
https://httpstat.us/500 ERROR ReadTimeout
https://notarealhost.xyz ERROR ConnectionError
````

## Exit codes

- `0` — every URL responded with a status below 400
- `1` — at least one URL returned 400 or above, was unreachable, or timed out

The exit code lets the script be used as a gate in a cron job or CI pipeline,
which can act on the result without parsing the output.

## Requirements

Python 3, `requests`
````
````

## Run with Docker

Build the image (run from this folder):

```bash
docker build -t healthchecker:1.0 .
```

Check one or more URLs:

```bash
docker run --rm healthchecker:1.0 https://google.com https://github.com
```

```
https://google.com 200 0.142
https://github.com 200 0.231
```

Run with no arguments to check the default URL (https://google.com):

```bash
docker run --rm healthchecker:1.0
```

The exit code is non-zero if any URL fails, so it can be used as a check in CI pipelines:

```bash
docker run --rm healthchecker:1.0 https://this-does-not-exist.invalid; echo "exit code: $?"
```

```
https://this-does-not-exist.invalid ERROR ConnectionError
exit code: 1
```

> **Note:** inside a container, `localhost` refers to the container itself.
> To check a service running on your own machine, use `host.docker.internal` instead.

### Image design

- Based on `python:3.12-slim` to keep the image small
- Dependencies installed before the script is copied, so code changes rebuild in seconds
- Runs as a non-root user (`appuser`)
- `ENTRYPOINT` runs the script; any URLs passed to `docker run` replace the default in `CMD`
