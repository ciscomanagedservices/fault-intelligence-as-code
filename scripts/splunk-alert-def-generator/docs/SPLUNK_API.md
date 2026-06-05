# Splunk REST API via Python (port 8089)

The Splunk management API runs on port 8089 (HTTPS). You can interact with it via the official **Splunk SDK for Python** (`splunk-sdk`) or directly with `requests`. Both approaches are covered below.

---

## Prerequisites

1. Container running with port 8089 published:

   ```bash
   docker run -d -p 8000:8000 -p 8089:8089 \
     -e "SPLUNK_PASSWORD=changeme" \
     --name splunk splunk-docker
   ```

2. Python 3.x installed on your host machine.

3. Install the dependencies:

   ```bash
   pip install splunk-sdk requests
   ```

---

## Option A — Splunk SDK for Python

The SDK handles authentication, session management, and result parsing.

### `test_splunk_sdk.py`

```python
import splunklib.client as client
import splunklib.results as results
import time

SERVICE = dict(
    host="localhost",
    port=8089,
    username="admin",
    password="changeme",
    # Splunk uses a self-signed cert by default; disable verification for local dev
    verify=False,
)

def main():
    # 1. Connect
    svc = client.connect(**SERVICE)
    print(f"Connected — Splunk build: {svc.info['build']}")

    # 2. List installed apps
    print("\nInstalled apps:")
    for app in svc.apps.list():
        print(f"  - {app.name}")

    # 3. Run a one-shot search (returns results directly)
    print("\nOne-shot search: index=_internal | head 5")
    search_query = "search index=_internal | head 5"
    oneshot_results = svc.jobs.oneshot(search_query, output_mode="json")

    reader = results.JSONResultsReader(oneshot_results)
    for result in reader:
        if isinstance(result, results.Message):
            print(f"  [message] {result.type}: {result.message}")
        elif isinstance(result, dict):
            print(f"  {result.get('_time', '')} — {result.get('_raw', '')[:120]}")

    # 4. Async search job example
    print("\nAsync search job: index=_internal earliest=-1m | stats count by source")
    job = svc.jobs.create("search index=_internal earliest=-1m | stats count by source")
    while not job.is_done():
        time.sleep(0.5)
        job.refresh()

    async_results = job.results(output_mode="json")
    reader = results.JSONResultsReader(async_results)
    for result in reader:
        if isinstance(result, dict):
            print(f"  {result}")

    job.cancel()


if __name__ == "__main__":
    main()
```

Run it:

```bash
python test_splunk_sdk.py
```

---

## Option B — Raw REST API with `requests`

Use this when you want to call specific endpoints without the SDK abstraction.

### `test_splunk_rest.py`

```python
import requests
import urllib3

# Suppress SSL warnings for the self-signed cert used by default
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://localhost:8089"
AUTH = ("admin", "changeme")


def main():
    # 1. Verify the service is up — /services/server/info
    resp = requests.get(
        f"{BASE_URL}/services/server/info",
        auth=AUTH,
        params={"output_mode": "json"},
        verify=False,
    )
    resp.raise_for_status()
    info = resp.json()["entry"][0]["content"]
    print(f"Splunk version : {info['version']}")
    print(f"Build          : {info['build']}")
    print(f"OS             : {info['os_name']} {info['cpu_arch']}")

    # 2. List installed apps
    resp = requests.get(
        f"{BASE_URL}/services/apps/local",
        auth=AUTH,
        params={"output_mode": "json", "count": 0},
        verify=False,
    )
    resp.raise_for_status()
    apps = [e["name"] for e in resp.json()["entry"]]
    print(f"\nInstalled apps ({len(apps)}): {', '.join(apps)}")

    # 3. Run a one-shot search
    print("\nOne-shot search: index=_internal | head 3")
    resp = requests.post(
        f"{BASE_URL}/services/search/jobs/export",
        auth=AUTH,
        data={
            "search": "search index=_internal | head 3",
            "output_mode": "json",
        },
        verify=False,
        stream=True,
    )
    resp.raise_for_status()
    for line in resp.iter_lines():
        if line:
            import json
            event = json.loads(line)
            if event.get("result"):
                raw = event["result"].get("_raw", "")[:120]
                print(f"  {raw}")


if __name__ == "__main__":
    main()
```

Run it:

```bash
python test_splunk_rest.py
```

---

## Key API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/services/server/info` | GET | Server version, build, OS info |
| `/services/apps/local` | GET | List installed apps |
| `/services/search/jobs` | POST | Create an async search job |
| `/services/search/jobs/export` | POST | One-shot streaming search |
| `/services/search/jobs/{sid}` | GET | Poll job status |
| `/services/search/jobs/{sid}/results` | GET | Fetch job results |
| `/services/authentication/users` | GET | List users |
| `/services/kvstore/status` | GET | KV store status |

---

## Notes

- **SSL**: Splunk uses a self-signed certificate on port 8089. Pass `verify=False` for local lab work, or mount a trusted certificate for shared labs.
- **Authentication**: Both basic auth (username/password) and token-based auth (`Authorization: Splunk <token>`) are supported. Prefer tokens for shared labs.
- **Default password**: The Dockerfile sets `SPLUNK_PASSWORD=changeme`. Always override this in non-lab environments.
- **Wait for readiness**: The container takes ~30–60 seconds to become ready after `docker run`. The API will return connection errors until Splunk finishes initializing.
