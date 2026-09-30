# healthchecker

A command line script that checks the health of a list of URLs. It reports
the status code and latency for each, and the error type for any that fail.

## Usage

````
python3 healthchecker.py url1 url2 url3 ...
````

At least one URL is required.

## Example

````
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

Save it, then push. That closes Week 4.