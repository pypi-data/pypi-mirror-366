from urllib.parse import urljoin

import requests

BASE_URL = "http://localhost:8000"
APPLICATION_FILEPATH = "tests/e2e/e01_minimal/app.py"


def test_app(app_process_factory):
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
        expect = {"is_configured": False, "is_running": False}
        assert res.status_code == 200
        assert res.json() == expect

        res = requests.post(urljoin(BASE_URL, "/strategy/start"))
        expect = {"detail": "Missing strategy configuration"}
        assert res.status_code == 400
        assert res.json() == expect

        res = requests.post(urljoin(BASE_URL, "/strategy/stop"))
        expect = {"detail": "Missing strategy configuration"}
        assert res.status_code == 400
        assert res.json() == expect

        # >> monitors

        res = requests.get(urljoin(BASE_URL, "/monitors"))
        expect = {"is_configured": False}
        assert res.status_code == 200
        assert res.json() == expect

        res = requests.post(urljoin(BASE_URL, "/monitors/start"))
        expect = {"detail": "Missing monitors configuration"}
        assert res.status_code == 400
        assert res.json() == expect

        res = requests.post(urljoin(BASE_URL, "/monitors/stop"))
        expect = {"detail": "Missing monitors configuration"}
        assert res.status_code == 400
        assert res.json() == expect

        # >> clock

        res = requests.get(urljoin(BASE_URL, "/clock"))
        assert res.status_code == 200
        assert res.json()["is_real"]

        res = requests.post(urljoin(BASE_URL, "/clock/start"))
        expect = {"detail": "Clock is not mock"}
        assert res.status_code == 400
        assert res.json() == expect

        res = requests.post(urljoin(BASE_URL, "/clock/stop"))
        expect = {"detail": "Clock is not mock"}
        assert res.status_code == 400
        assert res.json() == expect

    finally:
        proc.terminate()
        proc.wait()
