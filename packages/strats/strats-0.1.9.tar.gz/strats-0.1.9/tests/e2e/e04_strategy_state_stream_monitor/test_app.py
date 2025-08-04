import asyncio
import queue
import re
import threading
import time
from urllib.parse import urljoin

import pytest
import requests

BASE_URL = "http://localhost:8000"
APPLICATION_FILEPATH = "tests/e2e/e04_strategy_state_stream_monitor/app.py"


@pytest.mark.asyncio
async def test_app(app_process_factory):
    proc = app_process_factory(APPLICATION_FILEPATH)

    try:
        # >> healthz, metrics

        res = requests.get(urljoin(BASE_URL, "/healthz"))
        assert res.status_code == 200
        assert res.json() == "ok"

        res = requests.get(urljoin(BASE_URL, "/metrics"))
        assert res.status_code == 200

        # >> strategy

        res = requests.get(urljoin(BASE_URL, "/strategy"))
        expect = {"is_configured": True, "is_running": False}
        assert res.status_code == 200
        assert res.json() == expect

        # >> monitors

        res = requests.get(urljoin(BASE_URL, "/monitors"))
        expect = {
            "is_configured": True,
            "monitors": {
                "StreamMonitor_1": {
                    "is_running": False,
                },
            },
        }
        assert res.status_code == 200
        assert res.json() == expect

        # >> run

        res = requests.post(urljoin(BASE_URL, "/strategy/start"))
        expect = {"is_configured": True, "is_running": True}
        assert res.status_code == 200
        resjson = res.json()
        del resjson["started_at"]  # remove time
        assert resjson == expect

        res = requests.post(urljoin(BASE_URL, "/monitors/start"))
        expect = {
            "is_configured": True,
            "monitors": {
                "StreamMonitor_1": {
                    "is_running": True,
                },
            },
        }
        assert res.status_code == 200
        resjson = res.json()
        del resjson["monitors"]["StreamMonitor_1"]["started_at"]  # remove time
        assert resjson == expect

        await asyncio.sleep(0.5)

        # >> check

        res = requests.get(urljoin(BASE_URL, "/metrics"))
        assert res.status_code == 200
        assert extract_unlabeled_metric_value(res.text, "prices_bid") == 100.0
        assert extract_unlabeled_metric_value(res.text, "prices_ask") == 101.0
        assert extract_unlabeled_metric_value(res.text, "prices_spread") == 1.0
        assert extract_unlabeled_metric_value(res.text, "prices_update_count_total") == 1.0

        stderrs = get_stderr_list(proc)
        assert "INFO : __main__ : strategy > bid: 100" in stderrs[-1]

        # >> stop

        res = requests.post(urljoin(BASE_URL, "/monitors/stop"))
        expect = {
            "is_configured": True,
            "monitors": {
                "StreamMonitor_1": {
                    "is_running": False,
                },
            },
        }
        assert res.status_code == 200
        assert res.json() == expect

        res = requests.post(urljoin(BASE_URL, "/strategy/stop"))
        expect = {"is_configured": True, "is_running": False}
        assert res.status_code == 200
        assert res.json() == expect

    finally:
        proc.terminate()
        proc.wait()


def extract_unlabeled_metric_value(body: str, metric_name: str) -> float:
    pattern = rf"^{re.escape(metric_name)} ([0-9.e+-]+)"
    match = re.search(pattern, body, re.MULTILINE)
    if not match:
        raise ValueError(f"Metric {metric_name} not found")
    return float(match.group(1))


def read_stderr_lines(process, output_queue):
    for line in process.stderr:
        output_queue.put(line)
    output_queue.put(None)  # signal end of stream


def get_stderr_list(process, timeout=1) -> list[str]:
    stderrs = []

    q: queue.Queue = queue.Queue()
    t = threading.Thread(target=read_stderr_lines, args=(process, q), daemon=True)
    t.start()

    start_time = time.time()
    while True:
        try:
            line = q.get(timeout=0.1)
            if line is None:  # end of stream
                break
            stderrs.append(line.strip())
        except queue.Empty:
            if time.time() - start_time > timeout:
                break
    return stderrs
