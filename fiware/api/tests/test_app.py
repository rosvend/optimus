import json
from datetime import datetime, timezone

import pytest

from app import create_app
from orion import BackendError

KEY = "secret-key"
NOW = datetime(2026, 10, 14, 15, 0, 0, tzinfo=timezone.utc)
READING = {"temperature": 22.5, "humidity": 60, "lat": 6.24, "lon": -75.58}


class FakeOrion:
    def __init__(self, fail=False):
        self.readings = []
        self.fail = fail

    def publish(self, readings):
        if self.fail:
            raise BackendError("down")
        self.readings.extend(readings)


class FakeHistory:
    """Mimics QuantumLeap + CrateDB: answers queries from what was published to the fake Orion."""

    def __init__(self, orion):
        self.orion = orion

    def query(self, query):
        fields = ("lat", "lon") if query.sensor == "gps" else (query.sensor,)
        matches = [r for r in self.orion.readings if fields[0] in r]
        matches.sort(key=lambda r: r["ts"], reverse=True)
        return [{"ts": r["ts"], **{f: r[f] for f in fields}} for r in matches[:query.limit]]


@pytest.fixture
def orion():
    return FakeOrion()


@pytest.fixture
def client(orion):
    return create_app(orion, FakeHistory(orion), KEY, now=lambda: NOW).test_client()


def post(client, body, key=KEY):
    headers = {"x-api-key": key} if key is not None else {}
    data = json.dumps(body) if isinstance(body, dict) else body
    return client.post("/api/readings", data=data, headers=headers, content_type="application/json")


def get(client, key=KEY, **params):
    return client.get("/api/readings", query_string=params, headers={"x-api-key": key})


def test_post_publishes_every_reading(client, orion):
    response = post(client, {"readings": [READING, {"temperature": 23}]})

    assert response.status_code == 200
    assert response.get_json() == {"stored": 2}
    assert [r["temperature"] for r in orion.readings] == [22.5, 23]


def test_missing_key_is_unauthorized(client, orion):
    response = post(client, {"readings": [READING]}, key=None)

    assert response.status_code == 401
    assert orion.readings == []


def test_wrong_key_is_unauthorized(client):
    assert get(client, key="nope", sensor="gps").status_code == 401


def test_header_name_is_case_insensitive(client):
    response = client.get("/api/readings", query_string={"sensor": "gps"}, headers={"X-Api-Key": KEY})

    assert response.status_code == 200


def test_invalid_post_returns_validation_status(client):
    response = post(client, "not json")

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_backend_failure_is_bad_gateway():
    app = create_app(FakeOrion(fail=True), None, KEY, now=lambda: NOW)

    response = post(app.test_client(), {"readings": [READING]})

    assert response.status_code == 502


def test_get_returns_stored_items_newest_first(client):
    post(client, {"readings": [{"lat": 1, "lon": 2, "age_ms": 1000}, {"lat": 3, "lon": 4}]})

    response = get(client, sensor="gps")

    assert response.status_code == 200
    items = response.get_json()["items"]
    assert [(i["lat"], i["lon"]) for i in items] == [(3, 4), (1, 2)]
    assert items[0]["ts"] == "2026-10-14T15:00:00.000Z"


def test_get_unknown_sensor_is_bad_request(client):
    assert get(client, sensor="pressure").status_code == 400


def test_other_methods_are_not_allowed(client):
    assert client.delete("/api/readings", headers={"x-api-key": KEY}).status_code == 405


def test_cors_preflight_needs_no_key(client):
    response = client.options("/api/readings")

    assert response.status_code == 200
    assert response.headers["Access-Control-Allow-Origin"] == "*"
    assert "x-api-key" in response.headers["Access-Control-Allow-Headers"]


def test_dashboard_config_points_at_the_api_and_signaling(client):
    assert client.get("/config.json", base_url="http://robot.example").get_json() == {
        "apiUrl": "api/readings",
        "signalingUrl": "ws://robot.example/signaling",
        "roomId": "OPTIMUS",
    }


def test_dashboard_config_uses_secure_websockets_over_https(client):
    assert client.get("/config.json", base_url="https://robot.example").get_json()["signalingUrl"] == "wss://robot.example/signaling"


def test_signaling_handshake_requires_the_api_key(client):
    assert client.get("/signaling", query_string={"key": "wrong"}).status_code == 401
    assert client.get("/signaling").status_code == 401
