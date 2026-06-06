import splunklib.client as client
import splunklib.results as results
import time

SERVICE = dict(
    host="127.0.0.1",
    port=8089,
    username="admin",
    password="clus26demo",
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
